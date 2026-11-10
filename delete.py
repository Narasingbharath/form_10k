"""
Simplified 10-K Form Parser - Single Agent Approach
Avoids complex multi-agent coordination issues
"""

from crewai import Crew, Agent, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from typing import List, Optional
from pydantic import BaseModel, Field
import json
import os
#import boto3
from crewai import LLM
import re
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
import boto3
# AWS Bedrock configuration
# Ollama local model configuration
# ollama_llm = LLM(
#     model="ollama/phi3:mini",
#     base_url="http://localhost:11434",
#     temperature=0.2,
#     max_tokens=2048,
# )

# Set AWS credentials
os.environ["AWS_ACCESS_KEY_ID"] = "AKIA6QKHEVBYCDYZQNN3"# Replace with your actual key
os.environ["AWS_SECRET_ACCESS_KEY"] = "u1wBrSzq911FoRsCn+cE2DybdZ7TySz3ei71OBZN" # Replace with your actual key
os.environ["AWS_REGION_NAME"] = "us-east-1"

# Initialize AWS Bedrock client
bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name="us-east-1",
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
)

# Use Bedrock LLM with CrewAI
bedrock_llm = LLM(
    model="bedrock/us.meta.llama4-maverick-17b-instruct-v1:0",
    temperature=0.2,
    max_tokens=2048,
)

# ============================================================================
# SIMPLIFIED PYDANTIC MODELS FOR FORM 10-K
# ============================================================================

class CoverPageSecurities(BaseModel):
    title_of_each_class: Optional[str] = Field(None, description="Title of each class")
    trading_symbols: Optional[str] = Field(None, description="Trading Symbol(s)")
    name_of_each_exchange: Optional[str] = Field(None, description="Name of each exchange on which registered")

class CoverPage(BaseModel):
    form_type: Optional[str] = Field(None, description="Form Type")
    fiscal_year_ended: Optional[str] = Field(None, description="For the fiscal year ended")
    commission_file_number: Optional[str] = Field(None, description="Commission file number")
    registrant_name: Optional[str] = Field(None, description="Exact name of registrant as specified in its charter")
    state_of_incorporation: Optional[str] = Field(None, description="State or other jurisdiction of incorporation")
    irs_employer_identification_number: Optional[str] = Field(None, description="I.R.S. Employer Identification No.")
    address_of_principal_executive_offices: Optional[str] = Field(None, description="Address of principal executive offices")
    registrant_telephone_number: Optional[str] = Field(None, description="Registrant's telephone number")
    securities: Optional[List[CoverPageSecurities]] = Field(None, description="Securities registered")

class CompanyOverview(BaseModel):
    company_description: Optional[str] = Field(None, description="Company description")
    key_priorities: Optional[str] = Field(None, description="Key strategic priorities")

class Products(BaseModel):
    product_overview: Optional[str] = Field(None, description="Product portfolio overview")
    analog_and_mixed_signal: Optional[str] = Field(None, description="Analog and Mixed Signal products")

class Markets(BaseModel):
    industrial_percent_2024: Optional[str] = Field(None, description="Industrial percent of fiscal 2024 revenue")
    automotive_percent_2024: Optional[str] = Field(None, description="Automotive percent of fiscal 2024 revenue")
    communications_percent_2024: Optional[str] = Field(None, description="Communications percent of fiscal 2024 revenue")
    consumer_percent_2024: Optional[str] = Field(None, description="Consumer percent of fiscal 2024 revenue")

class Item1Business(BaseModel):
    company_overview: Optional[CompanyOverview] = Field(None, description="Company Overview")
    products: Optional[Products] = Field(None, description="Products")
    markets: Optional[Markets] = Field(None, description="Markets")

class PartI(BaseModel):
    item_1_business: Optional[Item1Business] = Field(None, description="Item 1. Business")

class ConsolidatedStatementsOfIncome(BaseModel):
    revenue: Optional[str] = Field(None, description="Revenue")
    net_income: Optional[str] = Field(None, description="Net income")
    basic_earnings_per_share: Optional[str] = Field(None, description="Basic earnings per common share")
    diluted_earnings_per_share: Optional[str] = Field(None, description="Diluted earnings per common share")

class ConsolidatedBalanceSheets(BaseModel):
    total_assets: Optional[str] = Field(None, description="TOTAL ASSETS")
    total_current_assets: Optional[str] = Field(None, description="Total current assets")
    total_shareholders_equity: Optional[str] = Field(None, description="Total shareholders' equity")

class ConsolidatedStatementsOfCashFlows(BaseModel):
    net_cash_provided_by_operating_activities: Optional[str] = Field(None, description="Net cash provided by operating activities")
    net_cash_used_for_investing_activities: Optional[str] = Field(None, description="Net cash used for investing activities")
    net_cash_used_for_financing_activities: Optional[str] = Field(None, description="Net cash used for financing activities")

class Item8FinancialStatements(BaseModel):
    consolidated_statements_of_income: Optional[ConsolidatedStatementsOfIncome] = Field(None, description="Consolidated Statements of Income")
    consolidated_balance_sheets: Optional[ConsolidatedBalanceSheets] = Field(None, description="Consolidated Balance Sheets")
    consolidated_statements_cash_flows: Optional[ConsolidatedStatementsOfCashFlows] = Field(None, description="Consolidated Statements of Cash Flows")

class PartII(BaseModel):
    item_8_financial_statements: Optional[Item8FinancialStatements] = Field(None, description="Item 8. Financial Statements")

class Form10K(BaseModel):
    cover_page: Optional[CoverPage] = Field(None, description="Cover page")
    part_i: Optional[PartI] = Field(None, description="PART I")
    part_ii: Optional[PartII] = Field(None, description="PART II")

# ============================================================================
# RESULT PARSING UTILITIES
# ============================================================================

def extract_json_from_text(text: str) -> dict:
    """Extract JSON from text that might contain other content"""
    if not text:
        return {}
    
    # Try to parse as direct JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Look for JSON blocks in the text
    json_patterns = [
        r'```json\s*(.*?)\s*```',  # JSON in code blocks
        r'```\s*(.*?)\s*```',      # Generic code blocks
        r'\{.*\}',                 # Any JSON-like structure
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    print(f"Warning: Could not extract valid JSON from text: {text[:200]}...")
    return {}

def safe_get_result_content(result) -> str:
    """Safely extract content from CrewAI result"""
    try:
        if hasattr(result, 'raw'):
            return str(result.raw)
        elif hasattr(result, 'content'):
            return str(result.content)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    except Exception as e:
        print(f"Warning: Error extracting result content: {e}")
        return ""

# ============================================================================
# SIMPLIFIED SINGLE-AGENT PARSER
# ============================================================================

def clean_parsed_data(data: dict) -> dict:
    """Clean parsed data to match Pydantic model expectations"""
    if not data:
        return data
    
    # Fix securities trading_symbols if it's a list
    if data.get("cover_page") and data["cover_page"].get("securities"):
        for security in data["cover_page"]["securities"]:
            if isinstance(security.get("trading_symbols"), list):
                security["trading_symbols"] = ", ".join(security["trading_symbols"])
    
    # Fix part_i business section
    if data.get("part_i") and data["part_i"].get("item_1_business"):
        business = data["part_i"]["item_1_business"]
        
        # Fix company_overview.key_priorities if it's a list
        if business.get("company_overview") and isinstance(business["company_overview"].get("key_priorities"), list):
            business["company_overview"]["key_priorities"] = ", ".join(business["company_overview"]["key_priorities"])
        
        # Fix markets percentages if they're floats
        if business.get("markets"):
            markets = business["markets"]
            for key in ["industrial_percent_2024", "automotive_percent_2024", "communications_percent_2024", "consumer_percent_2024"]:
                if key in markets and isinstance(markets[key], (int, float)):
                    markets[key] = f"{markets[key]}%"
    
    return data

class Form10KParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = os.path.abspath(pdf_path)
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        print(f"Using PDF file: {self.pdf_path}")
        
        # Create knowledge directory if it doesn't exist
        knowledge_dir = os.path.join(os.path.dirname(__file__), 'knowledge')
        os.makedirs(knowledge_dir, exist_ok=True)
        
        # Copy file to knowledge directory if needed
        knowledge_file_path = os.path.join(knowledge_dir, os.path.basename(pdf_path))
        if not os.path.exists(knowledge_file_path):
            import shutil
            shutil.copy2(self.pdf_path, knowledge_file_path)
            print(f"Copied PDF to knowledge directory: {knowledge_file_path}")
        
        self.content_source = CrewDoclingSource(file_paths=[os.path.basename(pdf_path)])
        self.agent = self._create_agent()
        
    def _create_agent(self):
        return Agent(
            role="10-K Form Data Extractor",
            goal="Extract structured data from 10-K SEC filings and return valid JSON",
            backstory="""You are an expert financial document analyst specializing in SEC 10-K filings. 
            You extract key information including cover page details, business descriptions, and financial data.
            You MUST return only valid JSON format without any explanatory text, markdown, or other formatting.""",
            verbose=True,
            llm=bedrock_llm
        )
    
    def _create_task(self, section_name: str):
        """Create task for specific section"""
        
        task_descriptions = {
            'cover_page': """
                Extract ONLY cover page information from the 10-K filing. 
                Return ONLY valid JSON in this exact format:
                
                {
                    "form_type": "extracted form type",
                    "fiscal_year_ended": "extracted fiscal year",
                    "commission_file_number": "extracted file number",
                    "registrant_name": "extracted company name",
                    "state_of_incorporation": "extracted state",
                    "irs_employer_identification_number": "extracted EIN",
                    "address_of_principal_executive_offices": "extracted address",
                    "registrant_telephone_number": "extracted phone",
                    "securities": [
                        {
                            "title_of_each_class": "extracted class title",
                            "trading_symbols": "extracted symbol", 
                            "name_of_each_exchange": "extracted exchange"
                        }
                    ]
                }
                """,
            
            'business': """
                Extract ONLY Item 1 Business section information from the 10-K filing.
                Return ONLY valid JSON in this exact format:
                
                {
                    "company_overview": {
                        "company_description": "extracted company overview text",
                        "key_priorities": "extracted key strategic priorities"
                    },
                    "products": {
                        "product_overview": "extracted product portfolio overview",
                        "analog_and_mixed_signal": "extracted analog and mixed signal products description"
                    },
                    "markets": {
                        "industrial_percent_2024": "extracted industrial percentage",
                        "automotive_percent_2024": "extracted automotive percentage",
                        "communications_percent_2024": "extracted communications percentage", 
                        "consumer_percent_2024": "extracted consumer percentage"
                    }
                }
                """,
            
            'financial': """
                Extract ONLY financial data from Item 8 Financial Statements.
                Return ONLY valid JSON in this exact format:
                
                {
                    "consolidated_statements_of_income": {
                        "revenue": "extracted revenue figure",
                        "net_income": "extracted net income figure",
                        "basic_earnings_per_share": "extracted basic EPS",
                        "diluted_earnings_per_share": "extracted diluted EPS"
                    },
                    "consolidated_balance_sheets": {
                        "total_assets": "extracted total assets",
                        "total_current_assets": "extracted current assets", 
                        "total_shareholders_equity": "extracted shareholders equity"
                    },
                    "consolidated_statements_cash_flows": {
                        "net_cash_provided_by_operating_activities": "extracted operating cash flow",
                        "net_cash_used_for_investing_activities": "extracted investing cash flow",
                        "net_cash_used_for_financing_activities": "extracted financing cash flow"
                    }
                }
                """,
            
            'full': """
                Extract comprehensive 10-K data including cover page, business section, and financial statements.
                Return ONLY valid JSON in this exact format:
                
                {
                    "cover_page": {
                        "form_type": "extracted form type",
                        "fiscal_year_ended": "extracted fiscal year", 
                        "registrant_name": "extracted company name",
                        "securities": [
                            {
                                "title_of_each_class": "extracted class title",
                                "trading_symbols": "extracted symbol",
                                "name_of_each_exchange": "extracted exchange"
                            }
                        ]
                    },
                    "part_i": {
                        "item_1_business": {
                            "company_overview": {
                                "company_description": "extracted company overview",
                                "key_priorities": "extracted priorities"
                            },
                            "products": {
                                "product_overview": "extracted product overview"
                            },
                            "markets": {
                                "industrial_percent_2024": "extracted industrial %",
                                "automotive_percent_2024": "extracted automotive %"
                            }
                        }
                    },
                    "part_ii": {
                        "item_8_financial_statements": {
                            "consolidated_statements_of_income": {
                                "revenue": "extracted revenue",
                                "net_income": "extracted net income"
                            },
                            "consolidated_balance_sheets": {
                                "total_assets": "extracted total assets"
                            },
                            "consolidated_statements_cash_flows": {
                                "net_cash_provided_by_operating_activities": "extracted operating cash flow"
                            }
                        }
                    }
                }
                """
        }
        
        return Task(
            description=task_descriptions.get(section_name, task_descriptions['full']),
            agent=self.agent,
            expected_output="Valid JSON object only"
        )
    
    def parse_section(self, section_name: str = 'full') -> dict:
        """Parse specific section and return JSON data"""
        try:
            task = self._create_task(section_name)
            
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                knowledge_sources=[self.content_source],
                verbose=True
            )
            
            # DEBUG: Check if knowledge is loaded
            print(f"Knowledge sources: {len(self.content_source.chunks) if hasattr(self.content_source, 'chunks') else 'unknown'}")
            
            print(f"Parsing {section_name} section...")
            result = crew.kickoff()
            # ... rest of code
            # Process result
            raw_content = safe_get_result_content(result)
            
            print(f"Raw result type: {type(result)}")
            print(f"Raw result preview: {raw_content[:300]}...")
            
            # Extract JSON
            parsed_data = extract_json_from_text(raw_content)
            
            if not parsed_data:
                print(f"❌ No valid JSON found in {section_name} result")
                # Save raw result for debugging
                with open(f"debug_{section_name}_result.txt", "w") as f:
                    f.write(str(raw_content))
                print(f"Saved raw result to debug_{section_name}_result.txt")
            
            return parsed_data
            
        except Exception as e:
            print(f"❌ Error parsing {section_name}: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def parse(self) -> Optional[Form10K]:
        """Parse the complete 10-K and return Pydantic model"""
        try:
            # Parse complete document
            parsed_data = self.parse_section('full')
            
            if not parsed_data:
                return None
            
            # Clean data before validation
            parsed_data = clean_parsed_data(parsed_data)
            
            # Create Pydantic model
            print("Creating Pydantic model...")
            form_10k = Form10K(**parsed_data)
            
            print("✅ Successfully parsed 10-K to Pydantic model!")
            return form_10k
            
        except Exception as e:
            print(f"❌ Error creating Pydantic model: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None
# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def setup_knowledge_directory():
    """Ensure knowledge directory exists and contains the PDF"""
    current_dir = os.path.dirname(__file__)
    knowledge_dir = os.path.join(current_dir, 'knowledge')
    
    os.makedirs(knowledge_dir, exist_ok=True)
    print(f"Knowledge directory: {knowledge_dir}")
    
    pdf_files = [f for f in os.listdir(current_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in current directory.")
        return None
    
    pdf_file = pdf_files[0]
    source_path = os.path.join(current_dir, pdf_file)
    dest_path = os.path.join(knowledge_dir, pdf_file)
     
    if not os.path.exists(dest_path):
        import shutil
        shutil.copy2(source_path, dest_path)
        print(f"✅ Copied {pdf_file} to knowledge directory")
    else:
        print(f"✅ {pdf_file} already exists in knowledge directory")
    
    return pdf_file

def main():
    """Example usage of the simplified 10-K parser with GraphDB integration"""
    
    pdf_filename = setup_knowledge_directory()
    
    if not pdf_filename:
        return
    
    try:
        # Parse 10-K
        parser = Form10KParser(pdf_filename)
        
        print("\n" + "="*50)
        print("Parsing 10-K document...")
        
        parsed_10k = parser.parse()
        
        if parsed_10k:
            print(f"Company: {parsed_10k.cover_page.registrant_name if parsed_10k.cover_page else 'Not found'}")
            print(f"Fiscal Year: {parsed_10k.cover_page.fiscal_year_ended if parsed_10k.cover_page else 'Not found'}")
            
            if parsed_10k.part_i and parsed_10k.part_i.item_1_business:
                business = parsed_10k.part_i.item_1_business
                if business.company_overview:
                    print(f"Business Overview: {business.company_overview.company_description}")
            
            if parsed_10k.part_ii and parsed_10k.part_ii.item_8_financial_statements:
                financials = parsed_10k.part_ii.item_8_financial_statements
                if financials.consolidated_statements_of_income:
                    print(f"Revenue: {financials.consolidated_statements_of_income.revenue}")
                    print(f"Net Income: {financials.consolidated_statements_of_income.net_income}")
            
            # Save to JSON file
            with open("parsed_10k.json", "w") as f:
                json.dump(parsed_10k.model_dump(), f, indent=2)
            print("✅ Saved parsed 10-K to parsed_10k.json")
            
            # Convert to RDF
            from semantic import process_10k_with_reasoning
            print("\nConverting to RDF format...")
            rdf_graph = process_10k_with_reasoning(parsed_10k.model_dump())
            print(f"✅ Created RDF graph with {len(rdf_graph)} triples")
            
        else:
            print("❌ Failed to parse 10-K")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
