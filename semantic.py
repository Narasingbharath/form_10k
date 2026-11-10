"""
10-K Parser integrated with GraphDB for semantic reasoning
Architecture: Parse -> Structure -> Convert to RDF -> Store in GraphDB -> Apply Reasoning
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

# Define custom namespace for 10-K ontology
FORM10K = Namespace("http://example.org/form10k#")
COMPANY = Namespace("http://example.org/company#")
FINANCIAL = Namespace("http://example.org/financial#")

class GraphDB10KConverter:
    """Converts parsed 10-K Pydantic models to RDF triples for GraphDB"""
    
    def __init__(self, graphdb_endpoint: str = "http://localhost:7200"):
        self.graphdb_endpoint = graphdb_endpoint
        self.graph = Graph()
        
        # Bind namespaces
        self.graph.bind("form10k", FORM10K)
        self.graph.bind("company", COMPANY)
        self.graph.bind("financial", FINANCIAL)
        self.graph.bind("owl", OWL)
        
    def convert_cover_page_to_rdf(self, cover_page: dict, company_uri: URIRef):
        """Convert cover page data to RDF triples"""
        
        if not cover_page:
            return
        
        # Company basic info
        if cover_page.get("registrant_name"):
            self.graph.add((company_uri, RDFS.label, Literal(cover_page["registrant_name"])))
            self.graph.add((company_uri, RDF.type, COMPANY.PublicCompany))
        
        if cover_page.get("state_of_incorporation"):
            self.graph.add((company_uri, COMPANY.incorporatedIn, 
                          Literal(cover_page["state_of_incorporation"])))
        
        if cover_page.get("irs_employer_identification_number"):
            self.graph.add((company_uri, COMPANY.ein, 
                          Literal(cover_page["irs_employer_identification_number"])))
        
        # Securities info
        if cover_page.get("securities"):
            for sec in cover_page["securities"]:
                security_uri = URIRef(f"{company_uri}/security/{sec.get('trading_symbols', 'unknown')}")
                self.graph.add((security_uri, RDF.type, FINANCIAL.Security))
                self.graph.add((company_uri, COMPANY.hasSecurityListing, security_uri))
                
                if sec.get("trading_symbols"):
                    self.graph.add((security_uri, FINANCIAL.ticker, 
                                  Literal(sec["trading_symbols"])))
                
                if sec.get("name_of_each_exchange"):
                    self.graph.add((security_uri, FINANCIAL.listedOn, 
                                  Literal(sec["name_of_each_exchange"])))
    
    def convert_business_to_rdf(self, business_data: dict, company_uri: URIRef):
        """Convert Item 1 Business section to RDF triples"""
        
        if not business_data:
            return
        
        # Company overview
        if business_data.get("company_overview"):
            overview = business_data["company_overview"]
            if overview.get("company_description"):
                self.graph.add((company_uri, COMPANY.description, 
                              Literal(overview["company_description"])))
        
        # Products
        if business_data.get("products"):
            products = business_data["products"]
            if products.get("product_overview"):
                product_line_uri = URIRef(f"{company_uri}/product-line")
                self.graph.add((product_line_uri, RDF.type, COMPANY.ProductLine))
                self.graph.add((company_uri, COMPANY.offersProducts, product_line_uri))
                self.graph.add((product_line_uri, RDFS.comment, 
                              Literal(products["product_overview"])))
        
        # Market segments with percentages
        if business_data.get("markets"):
            markets = business_data["markets"]
            
            # Create market segment nodes with revenue percentages
            for market_type in ["industrial", "automotive", "communications", "consumer"]:
                percent_key = f"{market_type}_percent_2024"
                if markets.get(percent_key):
                    market_uri = URIRef(f"{company_uri}/market/{market_type}")
                    self.graph.add((market_uri, RDF.type, COMPANY.MarketSegment))
                    self.graph.add((company_uri, COMPANY.servesMarket, market_uri))
                    self.graph.add((market_uri, COMPANY.marketName, Literal(market_type)))
                    
                    # Extract percentage value
                    percent_str = markets[percent_key].replace("%", "")
                    try:
                        percent_value = float(percent_str)
                        self.graph.add((market_uri, COMPANY.revenuePercentage, 
                                      Literal(percent_value, datatype=XSD.float)))
                    except:
                        pass
    
    def convert_financials_to_rdf(self, financials: dict, company_uri: URIRef, fiscal_year: str):
        """Convert Item 8 Financial Statements to RDF triples"""
        
        if not financials:
            return
        
        # Create financial report node
        report_uri = URIRef(f"{company_uri}/financial-report/{fiscal_year}")
        self.graph.add((report_uri, RDF.type, FINANCIAL.FinancialReport))
        self.graph.add((company_uri, FINANCIAL.hasFinancialReport, report_uri))
        self.graph.add((report_uri, FINANCIAL.fiscalYear, Literal(fiscal_year)))
        
        # Income statement
        if financials.get("consolidated_statements_of_income"):
            income = financials["consolidated_statements_of_income"]
            
            if income.get("revenue"):
                self.graph.add((report_uri, FINANCIAL.revenue, 
                              Literal(income["revenue"])))
            
            if income.get("net_income"):
                self.graph.add((report_uri, FINANCIAL.netIncome, 
                              Literal(income["net_income"])))
            
            if income.get("basic_earnings_per_share"):
                self.graph.add((report_uri, FINANCIAL.basicEPS, 
                              Literal(income["basic_earnings_per_share"])))
        
        # Balance sheet
        if financials.get("consolidated_balance_sheets"):
            balance = financials["consolidated_balance_sheets"]
            
            if balance.get("total_assets"):
                self.graph.add((report_uri, FINANCIAL.totalAssets, 
                              Literal(balance["total_assets"])))
            
            if balance.get("total_shareholders_equity"):
                self.graph.add((report_uri, FINANCIAL.shareholdersEquity, 
                              Literal(balance["total_shareholders_equity"])))
        
        # Cash flow
        if financials.get("consolidated_statements_cash_flows"):
            cashflow = financials["consolidated_statements_cash_flows"]
            
            if cashflow.get("net_cash_provided_by_operating_activities"):
                self.graph.add((report_uri, FINANCIAL.operatingCashFlow, 
                              Literal(cashflow["net_cash_provided_by_operating_activities"])))
    
    def convert_10k_to_rdf(self, form_10k_data: dict) -> Graph:
        """Convert complete 10-K parsed data to RDF graph"""
        
        # Extract company identifier
        company_name = "unknown"
        if form_10k_data.get("cover_page") and form_10k_data["cover_page"].get("registrant_name"):
            company_name = form_10k_data["cover_page"]["registrant_name"].replace(" ", "_").replace(",", "")
        
        company_uri = URIRef(f"{COMPANY}{company_name}")
        
        # Convert each section
        if form_10k_data.get("cover_page"):
            self.convert_cover_page_to_rdf(form_10k_data["cover_page"], company_uri)
        
        if form_10k_data.get("part_i") and form_10k_data["part_i"].get("item_1_business"):
            self.convert_business_to_rdf(form_10k_data["part_i"]["item_1_business"], company_uri)
        
        fiscal_year = "2024"  # Extract from cover page in real implementation
        if form_10k_data.get("part_ii") and form_10k_data["part_ii"].get("item_8_financial_statements"):
            self.convert_financials_to_rdf(
                form_10k_data["part_ii"]["item_8_financial_statements"], 
                company_uri, 
                fiscal_year
            )
        
        return self.graph
    
    def save_to_file(self, filename: str, format: str = "turtle"):
        """Save RDF graph to file"""
        self.graph.serialize(destination=filename, format=format)
        print(f"Saved RDF graph to {filename}")
    
    def upload_to_graphdb(self, repository_name: str):
        """Upload RDF graph to GraphDB repository"""
        sparql = SPARQLWrapper(f"{self.graphdb_endpoint}/repositories/{repository_name}/statements")
        
        # Serialize graph to turtle format
        rdf_data = self.graph.serialize(format="turtle")
        
        sparql.setMethod("POST")
        sparql.setQuery(rdf_data)
        sparql.setRequestMethod("postdirectly")
        
        try:
            sparql.query()
            print(f"Successfully uploaded to GraphDB repository: {repository_name}")
        except Exception as e:
            print(f"Error uploading to GraphDB: {e}")

class GraphDBReasoner:
    """Apply reasoning queries on 10-K data stored in GraphDB"""
    
    def __init__(self, graphdb_endpoint: str = "http://localhost:7200", repository: str = "10k-forms"):
        self.endpoint = f"{graphdb_endpoint}/repositories/{repository}"
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)
    
    def query_companies_by_market_segment(self, market_segment: str, min_percentage: float = 0.0):
        """Find companies with significant presence in a market segment"""
        
        query = f"""
        PREFIX company: <http://example.org/company#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT ?companyName ?marketName ?percentage
        WHERE {{
            ?company a company:PublicCompany ;
                    rdfs:label ?companyName ;
                    company:servesMarket ?market .
            ?market company:marketName "{market_segment}" ;
                   company:revenuePercentage ?percentage .
            FILTER (?percentage >= {min_percentage})
        }}
        ORDER BY DESC(?percentage)
        """
        
        self.sparql.setQuery(query)
        return self.sparql.query().convert()
    
    def query_financial_ratios(self, company_name: str):
        """Calculate financial ratios using reasoning over stored data"""
        
        query = f"""
        PREFIX company: <http://example.org/company#>
        PREFIX financial: <http://example.org/financial#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?fiscalYear ?revenue ?netIncome ?totalAssets ?equity
        WHERE {{
            ?company a company:PublicCompany ;
                    rdfs:label ?companyName ;
                    financial:hasFinancialReport ?report .
            ?report financial:fiscalYear ?fiscalYear ;
                   financial:revenue ?revenue ;
                   financial:netIncome ?netIncome ;
                   financial:totalAssets ?totalAssets ;
                   financial:shareholdersEquity ?equity .
            FILTER (CONTAINS(?companyName, "{company_name}"))
        }}
        ORDER BY DESC(?fiscalYear)
        """
        
        self.sparql.setQuery(query)
        return self.sparql.query().convert()
    
    def infer_industry_peers(self, company_name: str):
        """Find peer companies based on similar market segment distributions"""
        
        query = f"""
        PREFIX company: <http://example.org/company#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?peerName (COUNT(?sharedMarket) as ?commonMarkets)
        WHERE {{
            ?targetCompany rdfs:label ?targetName ;
                          company:servesMarket ?targetMarket .
            ?targetMarket company:marketName ?marketName .
            FILTER (CONTAINS(?targetName, "{company_name}"))
            
            ?peerCompany a company:PublicCompany ;
                        rdfs:label ?peerName ;
                        company:servesMarket ?peerMarket .
            ?peerMarket company:marketName ?marketName .
            
            FILTER (?targetCompany != ?peerCompany)
            BIND(?peerMarket as ?sharedMarket)
        }}
        GROUP BY ?peerName
        ORDER BY DESC(?commonMarkets)
        LIMIT 10
        """
        
        self.sparql.setQuery(query)
        return self.sparql.query().convert()

# Custom OWL reasoning rules for 10-K data validation
CUSTOM_REASONING_RULES = """
# Rule 1: Infer company industry based on market segment dominance
# If a company has >40% revenue from a market segment, classify it in that industry

PREFIX company: <http://example.org/company#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

[IndustryClassification:
    (?company company:servesMarket ?market)
    (?market company:revenuePercentage ?percentage)
    greaterThan(?percentage, 40)
    (?market company:marketName ?industryName)
    ->
    (?company company:primaryIndustry ?industryName)
]

# Rule 2: Infer financial health indicator
# If net income is positive and operating cash flow is positive, company is "healthy"

PREFIX financial: <http://example.org/financial#>

[FinancialHealthPositive:
    (?report financial:netIncome ?netIncome)
    (?report financial:operatingCashFlow ?cashflow)
    greaterThan(?netIncome, 0)
    greaterThan(?cashflow, 0)
    ->
    (?report financial:healthStatus "Positive")
]

# Rule 3: Infer potential supply chain relationships
# If Company A serves automotive market and Company B manufactures automotive components,
# infer potential supplier relationship

[SupplyChainInference:
    (?companyA company:servesMarket ?marketA)
    (?marketA company:marketName "automotive")
    (?companyB company:producesComponent "automotive")
    ->
    (?companyB company:potentialSupplierTo ?companyA)
]
"""

# Usage example combining everything
def process_10k_with_reasoning(parsed_10k_json: dict):
    """
    Complete pipeline: Parse 10-K -> Convert to RDF -> Store in GraphDB -> Apply Reasoning
    """
    
    # Step 1: Convert parsed 10-K to RDF
    converter = GraphDB10KConverter()
    rdf_graph = converter.convert_10k_to_rdf(parsed_10k_json)
    
    # Step 2: Save RDF to file for inspection
    converter.save_to_file("10k_data.ttl", format="turtle")
    
    # Step 3: Upload to GraphDB (requires GraphDB running)
    # converter.upload_to_graphdb("10k-forms")
    
    # Step 4: Query with reasoning
    reasoner = GraphDBReasoner()
    
    # Example queries
    # industrial_companies = reasoner.query_companies_by_market_segment("industrial", min_percentage=30.0)
    # financial_data = reasoner.query_financial_ratios("Analog Devices")
    # peer_companies = reasoner.infer_industry_peers("Analog Devices")
    
    return rdf_graph

# Example: Load parsed 10-K JSON and process
if __name__ == "__main__":
    # Load your parsed 10-K data
    with open("parsed_10k.json", "r") as f:
        parsed_data = json.load(f)
    
    # Process with reasoning
    rdf_graph = process_10k_with_reasoning(parsed_data)
    
    print(f"Generated {len(rdf_graph)} RDF triples")
    print("\nSample triples:")
    for subj, pred, obj in list(rdf_graph)[:5]:
        print(f"{subj} -> {pred} -> {obj}")