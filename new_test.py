"""
Enhanced 10-K Form Parser - Professional Grade
Addresses authentication issues, improves parsing accuracy, and provides robust error handling
"""

import json
import os
import re
import logging
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import traceback
from datetime import datetime

# Third-party imports
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pydantic import BaseModel, Field, validator
from crewai import Crew, Agent, Task, LLM
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# ENHANCED PYDANTIC MODELS WITH VALIDATION
# ============================================================================

class CoverPageSecurities(BaseModel):
    title_of_each_class: Optional[str] = Field(None, description="Title of each class")
    trading_symbols: Optional[str] = Field(None, description="Trading Symbol(s)")
    name_of_each_exchange: Optional[str] = Field(None, description="Name of each exchange on which registered")

class CoverPage(BaseModel):
    form_type: Optional[str] = Field(None, description="Form Type (should be '10-K')")
    fiscal_year_ended: Optional[str] = Field(None, description="For the fiscal year ended")
    commission_file_number: Optional[str] = Field(None, description="Commission file number")
    registrant_name: str = Field(..., description="Exact name of registrant as specified in its charter")
    state_of_incorporation: Optional[str] = Field(None, description="State or other jurisdiction of incorporation")
    irs_employer_identification_number: Optional[str] = Field(None, description="I.R.S. Employer Identification No.")
    address_of_principal_executive_offices: Optional[str] = Field(None, description="Address of principal executive offices")
    registrant_telephone_number: Optional[str] = Field(None, description="Registrant's telephone number")
    securities: Optional[List[CoverPageSecurities]] = Field(default=[], description="Securities registered")
    
    @validator('form_type')
    def validate_form_type(cls, v):
        if v and v.strip().upper() != '10-K':
            logger.warning(f"Unexpected form type: {v}")
        return v

class CompanyOverview(BaseModel):
    company_description: Optional[str] = Field(None, description="Comprehensive company description")
    key_priorities: Optional[str] = Field(None, description="Key strategic priorities")
    primary_business: Optional[str] = Field(None, description="Primary business activities")
    competitive_advantages: Optional[str] = Field(None, description="Competitive advantages")

class Products(BaseModel):
    product_overview: Optional[str] = Field(None, description="Product portfolio overview")
    main_products: Optional[List[str]] = Field(default=[], description="List of main products/services")
    research_and_development: Optional[str] = Field(None, description="R&D activities and investments")

class Markets(BaseModel):
    market_segments: Optional[Dict[str, str]] = Field(default={}, description="Market segments and percentages")
    geographic_markets: Optional[Dict[str, str]] = Field(default={}, description="Geographic market breakdown")
    target_customers: Optional[str] = Field(None, description="Target customer base")

class RiskFactors(BaseModel):
    primary_risks: Optional[List[str]] = Field(default=[], description="Primary risk factors")
    market_risks: Optional[str] = Field(None, description="Market-related risks")
    operational_risks: Optional[str] = Field(None, description="Operational risks")

class Item1Business(BaseModel):
    company_overview: Optional[CompanyOverview] = Field(None, description="Company Overview")
    products: Optional[Products] = Field(None, description="Products and Services")
    markets: Optional[Markets] = Field(None, description="Markets and Competition")
    risk_factors: Optional[RiskFactors] = Field(None, description="Risk Factors")

class PartI(BaseModel):
    item_1_business: Optional[Item1Business] = Field(None, description="Item 1. Business")
    item_1a_risk_factors: Optional[str] = Field(None, description="Item 1A. Risk Factors")
    item_2_properties: Optional[str] = Field(None, description="Item 2. Properties")

class FinancialMetrics(BaseModel):
    """Financial metrics with proper validation"""
    revenue: Optional[str] = Field(None, description="Total revenue/net sales")
    cost_of_revenue: Optional[str] = Field(None, description="Cost of goods sold/revenue")
    gross_profit: Optional[str] = Field(None, description="Gross profit")
    operating_income: Optional[str] = Field(None, description="Operating income/loss")
    net_income: Optional[str] = Field(None, description="Net income/loss")
    basic_earnings_per_share: Optional[str] = Field(None, description="Basic earnings per common share")
    diluted_earnings_per_share: Optional[str] = Field(None, description="Diluted earnings per common share")
    
    @validator('revenue', 'net_income', pre=True)
    def validate_financial_figures(cls, v):
        if v and isinstance(v, str):
            # Clean common financial formatting
            cleaned = re.sub(r'[^\d\.\-\(\),]', '', v)
            if cleaned:
                return cleaned
        return v

class ConsolidatedStatementsOfIncome(FinancialMetrics):
    """Income statement specific fields"""
    pass

class ConsolidatedBalanceSheets(BaseModel):
    total_assets: Optional[str] = Field(None, description="TOTAL ASSETS")
    total_current_assets: Optional[str] = Field(None, description="Total current assets")
    total_current_liabilities: Optional[str] = Field(None, description="Total current liabilities")
    total_shareholders_equity: Optional[str] = Field(None, description="Total shareholders' equity")
    cash_and_equivalents: Optional[str] = Field(None, description="Cash and cash equivalents")

class ConsolidatedStatementsOfCashFlows(BaseModel):
    net_cash_provided_by_operating_activities: Optional[str] = Field(None, description="Net cash provided by operating activities")
    net_cash_used_for_investing_activities: Optional[str] = Field(None, description="Net cash used for investing activities")
    net_cash_used_for_financing_activities: Optional[str] = Field(None, description="Net cash used for financing activities")
    free_cash_flow: Optional[str] = Field(None, description="Free cash flow")

class Item8FinancialStatements(BaseModel):
    consolidated_statements_of_income: Optional[ConsolidatedStatementsOfIncome] = Field(None, description="Consolidated Statements of Income")
    consolidated_balance_sheets: Optional[ConsolidatedBalanceSheets] = Field(None, description="Consolidated Balance Sheets")
    consolidated_statements_cash_flows: Optional[ConsolidatedStatementsOfCashFlows] = Field(None, description="Consolidated Statements of Cash Flows")

class PartII(BaseModel):
    item_5_market_for_stock: Optional[str] = Field(None, description="Item 5. Market for Registrant's Common Equity")
    item_7_md_a: Optional[str] = Field(None, description="Item 7. Management's Discussion and Analysis")
    item_8_financial_statements: Optional[Item8FinancialStatements] = Field(None, description="Item 8. Financial Statements")

class Form10K(BaseModel):
    """Complete 10-K Form structure with validation"""
    cover_page: CoverPage = Field(..., description="Cover page information")
    part_i: Optional[PartI] = Field(None, description="PART I")
    part_ii: Optional[PartII] = Field(None, description="PART II")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Parsing metadata")
    
    def model_post_init(self, __context):
        """Post-initialization validation"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata['parsed_at'] = datetime.now().isoformat()
        self.metadata['parser_version'] = '2.0'

# ============================================================================
# ENHANCED LLM CONFIGURATION WITH FALLBACK
# ============================================================================

class LLMManager:
    """Manages LLM configuration with multiple fallback options"""
    
    def __init__(self):
        self.llm = None
        self.current_provider = None
        
    def setup_bedrock_llm(self) -> Optional[LLM]:
        """Setup AWS Bedrock LLM with proper error handling"""
        try:
            # Validate AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                logger.error("AWS credentials not found")
                return None
                
            # Test Bedrock access
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            # Create LLM instance
            bedrock_llm = LLM(
                model="bedrock/us.meta.llama4-maverick-17b-instruct-v1:0",
                temperature=0.1,  # Lower temperature for more consistent extraction
                max_tokens=4096,  # Increased token limit
            )
            
            logger.info("✅ Successfully configured AWS Bedrock LLM")
            self.current_provider = "bedrock"
            return bedrock_llm
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"AWS Bedrock setup failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error setting up Bedrock: {e}")
            return None
    
    def setup_openai_fallback(self) -> Optional[LLM]:
        """Setup OpenAI as fallback"""
        try:
            if os.getenv('OPENAI_API_KEY'):
                openai_llm = LLM(
                    model="gpt-4",
                    temperature=0.1,
                    max_tokens=4096,
                )
                logger.info("✅ Successfully configured OpenAI LLM as fallback")
                self.current_provider = "openai"
                return openai_llm
        except Exception as e:
            logger.error(f"OpenAI setup failed: {e}")
        return None
    
    def get_llm(self) -> LLM:
        """Get best available LLM"""
        if self.llm:
            return self.llm
            
        # Try Bedrock first
        self.llm = self.setup_bedrock_llm()
        
        # Fallback to OpenAI if Bedrock fails
        if not self.llm:
            logger.warning("Bedrock failed, trying OpenAI fallback...")
            self.llm = self.setup_openai_fallback()
        
        if not self.llm:
            raise RuntimeError("No LLM provider available. Check AWS credentials or set OPENAI_API_KEY.")
            
        return self.llm

# ============================================================================
# ENHANCED TEXT PROCESSING UTILITIES
# ============================================================================

class TextProcessor:
    """Enhanced text processing for better extraction"""
    
    @staticmethod
    def clean_financial_value(value: str) -> str:
        """Clean and standardize financial values"""
        if not value:
            return value
            
        # Remove common formatting but preserve meaningful content
        cleaned = re.sub(r'\s+', ' ', value.strip())
        return cleaned
    
    @staticmethod
    def extract_json_robustly(text: str) -> Dict[str, Any]:
        """Enhanced JSON extraction with multiple fallback strategies"""
        if not text or not text.strip():
            return {}
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from code blocks
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'<json>\s*(.*?)\s*</json>',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # Strategy 3: Find JSON-like structure
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Try to fix common JSON issues
        try:
            # Fix common issues like trailing commas, single quotes
            fixed_text = text.strip()
            fixed_text = re.sub(r',\s*}', '}', fixed_text)  # Remove trailing commas
            fixed_text = re.sub(r',\s*]', ']', fixed_text)
            fixed_text = re.sub(r"'([^']*)':", r'"\1":', fixed_text)  # Single to double quotes for keys
            
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            pass
        
        logger.warning(f"Failed to extract JSON from text: {text[:200]}...")
        return {}

# ============================================================================
# ENHANCED 10-K PARSER WITH BETTER PROMPTS AND ERROR HANDLING
# ============================================================================

class Enhanced10KParser:
    """Enhanced 10-K parser with improved accuracy and error handling"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path).resolve()
        self.text_processor = TextProcessor()
        self.llm_manager = LLMManager()
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        logger.info(f"Initializing parser for: {self.pdf_path}")
        
        # Setup knowledge source
        self.content_source = self._setup_knowledge_source()
        
        # Get LLM instance
        self.llm = self.llm_manager.get_llm()
        
        # Create agent
        self.agent = self._create_enhanced_agent()
    
    def _setup_knowledge_source(self) -> CrewDoclingSource:
        """Setup knowledge source with proper file handling"""
        try:
            # Use absolute path for knowledge source
            return CrewDoclingSource(file_paths=[str(self.pdf_path)])
        except Exception as e:
            logger.error(f"Failed to setup knowledge source: {e}")
            raise
    
    def _create_enhanced_agent(self) -> Agent:
        """Create agent with enhanced prompting"""
        return Agent(
            role="Expert SEC 10-K Financial Document Analyst",
            goal="""Extract precise, structured data from SEC 10-K filings with high accuracy. 
            Focus on factual information directly from the document without hallucination.""",
            backstory="""You are a seasoned financial analyst with 20+ years of experience analyzing SEC filings.
            You specialize in extracting structured data from 10-K forms with perfect accuracy.
            You read documents carefully and extract ONLY information that is explicitly stated.
            You NEVER make up or guess information that is not clearly present in the document.
            You return ONLY valid JSON without any explanatory text, comments, or markdown formatting.""",
            verbose=True,
            llm=self.llm,
            max_iter=3,  # Limit iterations to prevent infinite loops
        )
    
    def _create_enhanced_task(self, section_name: str) -> Task:
        """Create enhanced task with better prompts"""
        
        enhanced_prompts = {
            'cover_page': """
                TASK: Extract cover page information from the 10-K filing.
                
                INSTRUCTIONS:
                1. Look for the FIRST PAGE or COVER PAGE of the document
                2. Find form type (should be "10-K")
                3. Extract fiscal year ended date
                4. Find commission file number (format: XXX-XX-XXXXX)
                5. Extract exact registrant/company name
                6. Find state of incorporation
                7. Extract IRS Employer ID (XX-XXXXXXX format)
                8. Get principal executive offices address
                9. Find telephone number
                10. Extract securities information (stock classes, symbols, exchanges)
                
                CRITICAL: Extract ONLY information explicitly stated in the document.
                If information is not found, use null for that field.
                
                Return ONLY this JSON structure:
                {
                    "form_type": "10-K",
                    "fiscal_year_ended": "December 31, 2023",
                    "commission_file_number": "001-12345",
                    "registrant_name": "Exact Company Name As Written",
                    "state_of_incorporation": "Delaware",
                    "irs_employer_identification_number": "12-3456789",
                    "address_of_principal_executive_offices": "Full address as written",
                    "registrant_telephone_number": "(555) 123-4567",
                    "securities": [
                        {
                            "title_of_each_class": "Common Stock",
                            "trading_symbols": "SYMBOL",
                            "name_of_each_exchange": "NASDAQ Global Select Market"
                        }
                    ]
                }
                """,
            
            'business': """
                TASK: Extract business information from Item 1 "Business" section.
                
                INSTRUCTIONS:
                1. Locate "ITEM 1. BUSINESS" or similar section header
                2. Extract company overview and description
                3. Find information about products and services
                4. Look for market information and segments
                5. Extract any mentioned strategic priorities
                6. Find competitive positioning information
                
                CRITICAL: Extract ONLY information explicitly stated in Item 1.
                Summarize lengthy descriptions but keep key facts accurate.
                
                Return ONLY this JSON structure:
                {
                    "company_overview": {
                        "company_description": "What the company does, main business activities",
                        "key_priorities": "Strategic priorities mentioned",
                        "primary_business": "Core business description",
                        "competitive_advantages": "Mentioned competitive advantages"
                    },
                    "products": {
                        "product_overview": "Overview of products/services offered",
                        "main_products": ["List", "of", "main", "products"],
                        "research_and_development": "R&D activities mentioned"
                    },
                    "markets": {
                        "market_segments": {"segment1": "percentage", "segment2": "percentage"},
                        "geographic_markets": {"region1": "info", "region2": "info"},
                        "target_customers": "Target customer description"
                    }
                }
                """,
            
            'financial': """
                TASK: Extract financial data from Item 8 "Financial Statements and Supplementary Data".
                
                INSTRUCTIONS:
                1. Look for "ITEM 8" or "CONSOLIDATED STATEMENTS" sections
                2. Find Income Statement data (revenue, expenses, net income, EPS)
                3. Extract Balance Sheet data (assets, liabilities, equity)
                4. Get Cash Flow Statement data (operating, investing, financing)
                5. Look for the MOST RECENT fiscal year data
                6. Extract exact figures as presented (with $ and commas)
                
                CRITICAL: Extract ONLY the actual financial figures from the statements.
                Include currency symbols and formatting as shown in the document.
                
                Return ONLY this JSON structure:
                {
                    "consolidated_statements_of_income": {
                        "revenue": "$XX,XXX,XXX",
                        "cost_of_revenue": "$XX,XXX,XXX",
                        "gross_profit": "$XX,XXX,XXX",
                        "operating_income": "$XX,XXX,XXX",
                        "net_income": "$XX,XXX,XXX",
                        "basic_earnings_per_share": "$X.XX",
                        "diluted_earnings_per_share": "$X.XX"
                    },
                    "consolidated_balance_sheets": {
                        "total_assets": "$XX,XXX,XXX",
                        "total_current_assets": "$XX,XXX,XXX",
                        "total_current_liabilities": "$XX,XXX,XXX",
                        "total_shareholders_equity": "$XX,XXX,XXX",
                        "cash_and_equivalents": "$XX,XXX,XXX"
                    },
                    "consolidated_statements_cash_flows": {
                        "net_cash_provided_by_operating_activities": "$XX,XXX,XXX",
                        "net_cash_used_for_investing_activities": "($XX,XXX,XXX)",
                        "net_cash_used_for_financing_activities": "($XX,XXX,XXX)",
                        "free_cash_flow": "$XX,XXX,XXX"
                    }
                }
                """
        }
        
        return Task(
            description=enhanced_prompts.get(section_name, enhanced_prompts['business']),
            agent=self.agent,
            expected_output="Valid JSON object with extracted data only - no explanations or markdown"
        )
    
    def parse_section_with_retry(self, section_name: str, max_retries: int = 3) -> Dict[str, Any]:
        """Parse section with retry logic for better reliability"""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Parsing {section_name} section (attempt {attempt + 1}/{max_retries})")
                
                task = self._create_enhanced_task(section_name)
                
                crew = Crew(
                    agents=[self.agent],
                    tasks=[task],
                    knowledge_sources=[self.content_source],
                    verbose=False,  # Reduce noise
                    max_rpm=10,  # Rate limiting
                )
                
                result = crew.kickoff()
                
                # Extract content
                if hasattr(result, 'raw'):
                    raw_content = str(result.raw)
                elif hasattr(result, 'content'):
                    raw_content = str(result.content)
                else:
                    raw_content = str(result)
                
                # Process and validate JSON
                parsed_data = self.text_processor.extract_json_robustly(raw_content)
                
                if parsed_data:
                    logger.info(f"✅ Successfully parsed {section_name} section")
                    return parsed_data
                else:
                    logger.warning(f"⚠️ No valid JSON found in {section_name} result (attempt {attempt + 1})")
                    
                    # Save debug info
                    debug_file = f"debug_{section_name}_attempt_{attempt + 1}.txt"
                    with open(debug_file, "w", encoding='utf-8') as f:
                        f.write(f"Raw Result:\n{raw_content}\n")
                    logger.info(f"Saved debug info to {debug_file}")
                    
            except Exception as e:
                logger.error(f"❌ Error parsing {section_name} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Full traceback: {traceback.format_exc()}")
        
        logger.error(f"❌ Failed to parse {section_name} after {max_retries} attempts")
        return {}
    
    def parse_complete_10k(self) -> Optional[Form10K]:
        """Parse complete 10-K with comprehensive error handling"""
        try:
            logger.info("Starting comprehensive 10-K parsing...")
            
            # Parse each section
            sections_data = {}
            
            # Cover page (required)
            logger.info("Parsing cover page...")
            cover_data = self.parse_section_with_retry('cover_page')
            if not cover_data or 'registrant_name' not in cover_data:
                logger.error("Failed to extract required cover page data")
                return None
            sections_data['cover_page'] = cover_data
            
            # Business section
            logger.info("Parsing business section...")
            business_data = self.parse_section_with_retry('business')
            if business_data:
                sections_data['part_i'] = {'item_1_business': business_data}
            
            # Financial section
            logger.info("Parsing financial section...")
            financial_data = self.parse_section_with_retry('financial')
            if financial_data:
                sections_data['part_ii'] = {'item_8_financial_statements': financial_data}
            
            # Create Form10K instance
            logger.info("Creating validated 10-K model...")
            
            # Add metadata
            sections_data['metadata'] = {
                'parsing_success_rate': len([k for k, v in sections_data.items() if v and k != 'metadata']) / 3,
                'llm_provider': self.llm_manager.current_provider,
                'source_file': str(self.pdf_path.name)
            }
            
            form_10k = Form10K(**sections_data)
            
            logger.info("✅ Successfully created validated 10-K model")
            return form_10k
            
        except Exception as e:
            logger.error(f"❌ Critical error in complete parsing: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def save_results(self, form_10k: Form10K, output_file: str = "enhanced_10k_results.json"):
        """Save results with comprehensive formatting"""
        try:
            output_data = form_10k.model_dump()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Results saved to {output_file}")
            
            # Also save a summary
            summary = {
                "company_name": form_10k.cover_page.registrant_name,
                "fiscal_year": form_10k.cover_page.fiscal_year_ended,
                "form_type": form_10k.cover_page.form_type,
                "parsing_metadata": form_10k.metadata,
                "sections_parsed": {
                    "cover_page": bool(form_10k.cover_page),
                    "business": bool(form_10k.part_i and form_10k.part_i.item_1_business),
                    "financial": bool(form_10k.part_ii and form_10k.part_ii.item_8_financial_statements),
                }
            }
            
            with open("parsing_summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Summary saved to parsing_summary.json")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")

# ============================================================================
# MAIN EXECUTION WITH COMPREHENSIVE TESTING
# ============================================================================

def main():
    """Enhanced main function with comprehensive error handling"""
    
    try:
        # Find PDF files
        pdf_files = list(Path.cwd().glob("*.pdf"))
        
        if not pdf_files:
            logger.error("❌ No PDF files found in current directory")
            return
        
        pdf_file = pdf_files[0]
        logger.info(f"Using PDF file: {pdf_file}")
        
        # Initialize parser
        parser = Enhanced10KParser(pdf_file)
        
        # Parse 10-K
        logger.info("Starting enhanced 10-K parsing...")
        parsed_10k = parser.parse_complete_10k()
        
        if parsed_10k:
            # Display summary
            logger.info("=" * 60)
            logger.info("PARSING RESULTS SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Company: {parsed_10k.cover_page.registrant_name}")
            logger.info(f"Form Type: {parsed_10k.cover_page.form_type}")
            logger.info(f"Fiscal Year: {parsed_10k.cover_page.fiscal_year_ended}")
            
            if parsed_10k.part_i and parsed_10k.part_i.item_1_business:
                business = parsed_10k.part_i.item_1_business.company_overview
                if business and business.company_description:
                    logger.info(f"Business: {business.company_description[:100]}...")
            
            if parsed_10k.part_ii and parsed_10k.part_ii.item_8_financial_statements:
                financials = parsed_10k.part_ii.item_8_financial_statements
                if financials.consolidated_statements_of_income:
                    income = financials.consolidated_statements_of_income
                    logger.info(f"Revenue: {income.revenue or 'Not found'}")
                    logger.info(f"Net Income: {income.net_income or 'Not found'}")
            
            # Save results
            parser.save_results(parsed_10k)
            
            logger.info("✅ 10-K parsing completed successfully!")
            
        else:
            logger.error("❌ Failed to parse 10-K document")
            
    except Exception as e:
        logger.error(f"❌ Critical error in main execution: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()