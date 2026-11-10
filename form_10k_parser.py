"""
Complete 10-K Form Parser - Single File Implementation
All Pydantic models + CrewAI + Docling integration in one file
"""

from crewai import Crew, Agent, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from typing import List, Optional
from pydantic import BaseModel, Field
import json

# ============================================================================
# COMPLETE PYDANTIC MODELS FOR FORM 10-K
# ============================================================================

# Cover Page Models
class CoverPageSecurities(BaseModel):
    title_of_each_class: Optional[str] = Field(None, description="Title of each class")
    trading_symbols: Optional[str] = Field(None, description="Trading Symbol(s)")
    name_of_each_exchange: Optional[str] = Field(None, description="Name of each exchange on which registered")

class CoverPage(BaseModel):
    form_type: Optional[str] = Field(None, description="Form Type")
    is_annual_report: Optional[bool] = Field(None, description="Check mark for Annual Report")
    is_transition_report: Optional[bool] = Field(None, description="Check mark for Transition Report")
    fiscal_year_ended: Optional[str] = Field(None, description="For the fiscal year ended")
    commission_file_number: Optional[str] = Field(None, description="Commission file number")
    registrant_name: Optional[str] = Field(None, description="Exact name of registrant as specified in its charter")
    state_of_incorporation: Optional[str] = Field(None, description="State or other jurisdiction of incorporation or organization")
    irs_employer_identification_number: Optional[str] = Field(None, description="I.R.S. Employer Identification No.")
    address_of_principal_executive_offices: Optional[str] = Field(None, description="Address of principal executive offices")
    zip_code: Optional[str] = Field(None, description="Zip Code")
    registrant_telephone_number: Optional[str] = Field(None, description="Registrant's telephone number, including area code")
    securities: Optional[List[CoverPageSecurities]] = Field(None, description="Securities registered pursuant to Section 12(b) of the Act")
    securities_registered_pursuant_to_section_12g: Optional[str] = Field(None, description="Securities registered pursuant to section 12(g) of the Act")
    aggregate_market_value: Optional[str] = Field(None, description="Aggregate market value of the voting and non-voting common equity")
    common_shares_outstanding: Optional[str] = Field(None, description="Number of shares of common stock outstanding")
    documents_incorporated_by_reference: Optional[str] = Field(None, description="Documents incorporated by reference")

# Table of Contents Model
class TableOfContents(BaseModel):
    note_about_forward_looking_statements: Optional[str] = Field(None, description="Note about Forward-Looking Statements")
    part_i_items: Optional[List[str]] = Field(None, description="PART I items")
    part_ii_items: Optional[List[str]] = Field(None, description="PART II items")
    part_iii_items: Optional[List[str]] = Field(None, description="PART III items")
    part_iv_items: Optional[List[str]] = Field(None, description="PART IV items")
    signatures: Optional[str] = Field(None, description="Signatures")

class NoteAboutForwardLookingStatements(BaseModel):
    content: Optional[str] = Field(None, description="Note About Forward-Looking Statements content")

# PART I Models - Item 1 Business
class CompanyOverviewStrategyAndMission(BaseModel):
    company_description: Optional[str] = Field(None, description="Company description")
    intelligent_edge_focus: Optional[str] = Field(None, description="The Intelligent Edge focus")
    key_priorities: Optional[str] = Field(None, description="Key strategic priorities")
    incorporation_info: Optional[str] = Field(None, description="Incorporation and company information")

class AvailableInformation(BaseModel):
    website: Optional[str] = Field(None, description="Company website")
    sec_filings_availability: Optional[str] = Field(None, description="SEC filings availability")
    governance_documents: Optional[str] = Field(None, description="Corporate governance documents")
    website_disclaimer: Optional[str] = Field(None, description="Website content disclaimer")

class Products(BaseModel):
    semiconductor_overview: Optional[str] = Field(None, description="Semiconductor components overview")
    ic_description: Optional[str] = Field(None, description="Integrated circuits description")
    product_portfolio_overview: Optional[str] = Field(None, description="Product portfolio overview")
    analog_and_mixed_signal: Optional[str] = Field(None, description="Analog and Mixed Signal products")
    power_management_and_reference: Optional[str] = Field(None, description="Power Management & Reference products")
    amplifiers_rf_and_microwave: Optional[str] = Field(None, description="Amplifiers/RF and Microwave products")
    sensors_and_actuators: Optional[str] = Field(None, description="Sensors & Actuators products")
    digital_signal_processing: Optional[str] = Field(None, description="Digital Signal Processing and System Products (DSPs)")
    interface: Optional[str] = Field(None, description="Interface products")

class SalesChannel(BaseModel):
    sales_approach: Optional[str] = Field(None, description="Sales approach description")
    global_presence: Optional[str] = Field(None, description="Global sales presence")
    marketing_programs: Optional[str] = Field(None, description="Marketing and promotional programs")
    distributor_strategy: Optional[str] = Field(None, description="Distributor strategy")
    distributor_agreements: Optional[str] = Field(None, description="Distributor agreements and terms")
    customer_contracts: Optional[str] = Field(None, description="Customer contracts information")

class EndMarketBreakdown(BaseModel):
    industrial_percent_2024: Optional[str] = Field(None, description="Industrial percent of fiscal 2024 revenue")
    industrial_percent_2023: Optional[str] = Field(None, description="Industrial percent of fiscal 2023 revenue")
    industrial_percent_2022: Optional[str] = Field(None, description="Industrial percent of fiscal 2022 revenue")
    automotive_percent_2024: Optional[str] = Field(None, description="Automotive percent of fiscal 2024 revenue")
    automotive_percent_2023: Optional[str] = Field(None, description="Automotive percent of fiscal 2023 revenue")
    automotive_percent_2022: Optional[str] = Field(None, description="Automotive percent of fiscal 2022 revenue")
    communications_percent_2024: Optional[str] = Field(None, description="Communications percent of fiscal 2024 revenue")
    communications_percent_2023: Optional[str] = Field(None, description="Communications percent of fiscal 2023 revenue")
    communications_percent_2022: Optional[str] = Field(None, description="Communications percent of fiscal 2022 revenue")
    consumer_percent_2024: Optional[str] = Field(None, description="Consumer percent of fiscal 2024 revenue")
    consumer_percent_2023: Optional[str] = Field(None, description="Consumer percent of fiscal 2023 revenue")
    consumer_percent_2022: Optional[str] = Field(None, description="Consumer percent of fiscal 2022 revenue")

class IndustrialAutomation(BaseModel):
    overview: Optional[str] = Field(None, description="Industrial Automation overview")
    applications: Optional[List[str]] = Field(None, description="Industrial automation applications")

class InstrumentationAndMeasurement(BaseModel):
    overview: Optional[str] = Field(None, description="Instrumentation & Measurement overview")
    applications: Optional[List[str]] = Field(None, description="Instrumentation and measurement applications")

class AerospaceDefense(BaseModel):
    overview: Optional[str] = Field(None, description="Aerospace/Defense overview")
    applications: Optional[List[str]] = Field(None, description="Aerospace/Defense applications")

class Healthcare(BaseModel):
    overview: Optional[str] = Field(None, description="Healthcare market overview")
    applications: Optional[List[str]] = Field(None, description="Healthcare applications")

class EnergyManagement(BaseModel):
    overview: Optional[str] = Field(None, description="Energy Management overview")
    applications: Optional[List[str]] = Field(None, description="Energy management applications")

class Industrial(BaseModel):
    industrial_automation: Optional[IndustrialAutomation] = Field(None, description="Industrial Automation")
    instrumentation_and_measurement: Optional[InstrumentationAndMeasurement] = Field(None, description="Instrumentation & Measurement")
    aerospace_defense: Optional[AerospaceDefense] = Field(None, description="Aerospace/Defense")
    healthcare: Optional[Healthcare] = Field(None, description="Healthcare")
    energy_management: Optional[EnergyManagement] = Field(None, description="Energy Management")

class Automotive(BaseModel):
    overview: Optional[str] = Field(None, description="Automotive market overview")
    applications: Optional[List[str]] = Field(None, description="Automotive applications")

class Communications(BaseModel):
    overview: Optional[str] = Field(None, description="Communications market overview")
    applications: Optional[List[str]] = Field(None, description="Communications applications")

class Consumer(BaseModel):
    overview: Optional[str] = Field(None, description="Consumer market overview")
    applications: Optional[List[str]] = Field(None, description="Consumer applications")

class Markets(BaseModel):
    end_market_breakdown: Optional[EndMarketBreakdown] = Field(None, description="End market revenue breakdown")
    industrial: Optional[Industrial] = Field(None, description="Industrial end market")
    automotive: Optional[Automotive] = Field(None, description="Automotive end market")
    communications: Optional[Communications] = Field(None, description="Communications end market")
    consumer: Optional[Consumer] = Field(None, description="Consumer end market")

class Competition(BaseModel):
    competitive_factors: Optional[str] = Field(None, description="Competitive performance factors")
    competitor_overview: Optional[str] = Field(None, description="Competitor overview")
    competitive_advantages: Optional[str] = Field(None, description="Company competitive advantages")

class Seasonality(BaseModel):
    seasonality_patterns: Optional[str] = Field(None, description="Seasonality patterns")
    demand_assessment_factors: Optional[str] = Field(None, description="Demand assessment factors")
    backlog_definition: Optional[str] = Field(None, description="Backlog definition")
    order_cancellation_policy: Optional[str] = Field(None, description="Order cancellation policy")

class ProductionResources(BaseModel):
    manufacturing_process: Optional[str] = Field(None, description="Manufacturing process overview")
    raw_materials: Optional[str] = Field(None, description="Raw materials")
    manufacturing_facilities: Optional[str] = Field(None, description="Manufacturing facilities")
    third_party_suppliers: Optional[str] = Field(None, description="Third-party suppliers")

class PatentsAndIntellectualPropertyRights(BaseModel):
    ip_strategy: Optional[str] = Field(None, description="Intellectual property strategy")
    patent_portfolio: Optional[str] = Field(None, description="Patent portfolio")
    competitive_advantages: Optional[str] = Field(None, description="Competitive advantages")
    trademarks: Optional[str] = Field(None, description="Trademarks")

class GovernmentRegulation(BaseModel):
    regulatory_overview: Optional[str] = Field(None, description="Government regulation overview")

class EnvironmentSocialAndGovernance(BaseModel):
    esg_overview: Optional[str] = Field(None, description="ESG overview")
    oversight_structure: Optional[str] = Field(None, description="ESG oversight structure")
    ehs_management: Optional[str] = Field(None, description="Environment, health and safety management")
    certifications: Optional[str] = Field(None, description="EHS certifications")
    regulatory_compliance: Optional[str] = Field(None, description="Regulatory compliance")

class HumanCapitalAndEmpowerment(BaseModel):
    human_capital_philosophy: Optional[str] = Field(None, description="Human capital philosophy")
    diversity_and_inclusion: Optional[str] = Field(None, description="Diversity and inclusion")
    employee_networks: Optional[str] = Field(None, description="Employee networks")
    workforce_statistics: Optional[str] = Field(None, description="Workforce statistics")
    compensation_philosophy: Optional[str] = Field(None, description="Compensation philosophy")
    benefits: Optional[str] = Field(None, description="Employee benefits")
    employee_surveys: Optional[str] = Field(None, description="Employee surveys and recognition")

class Item1Business(BaseModel):
    company_overview_strategy_and_mission: Optional[CompanyOverviewStrategyAndMission] = Field(None, description="Company Overview, Strategy and Mission")
    available_information: Optional[AvailableInformation] = Field(None, description="Available Information")
    products: Optional[Products] = Field(None, description="Products")
    sales_channel: Optional[SalesChannel] = Field(None, description="Sales Channel")
    markets: Optional[Markets] = Field(None, description="Markets")
    competition: Optional[Competition] = Field(None, description="Competition")
    seasonality: Optional[Seasonality] = Field(None, description="Seasonality")
    production_resources: Optional[ProductionResources] = Field(None, description="Production Resources")
    patents_and_intellectual_property_rights: Optional[PatentsAndIntellectualPropertyRights] = Field(None, description="Patents and Intellectual Property Rights")
    government_regulation: Optional[GovernmentRegulation] = Field(None, description="Government Regulation")
    environment_social_and_governance: Optional[EnvironmentSocialAndGovernance] = Field(None, description="Environment, Social and Governance")
    human_capital_and_empowerment: Optional[HumanCapitalAndEmpowerment] = Field(None, description="Human Capital and Empowerment")

# Risk Factors Models
class RisksRelatedToBusiness(BaseModel):
    global_political_economic_uncertainty: Optional[str] = Field(None, description="Global political and economic uncertainty risks")
    cyclical_markets: Optional[str] = Field(None, description="Cyclical semiconductor market risks")
    third_party_supply_reliance: Optional[str] = Field(None, description="Third party supply chain risks")
    product_diversion_risks: Optional[str] = Field(None, description="Product diversion and gray market risks")
    manufacturing_disruption_risks: Optional[str] = Field(None, description="Manufacturing disruption risks")
    distributor_dependence: Optional[str] = Field(None, description="Distributor performance dependence")
    innovation_execution_risks: Optional[str] = Field(None, description="Innovation and execution risks")
    financial_forecasting_risks: Optional[str] = Field(None, description="Financial forecasting and fluctuation risks")
    competitive_risks: Optional[str] = Field(None, description="Competitive market risks")
    key_personnel_risks: Optional[str] = Field(None, description="Key personnel recruitment and retention risks")
    customer_commitment_risks: Optional[str] = Field(None, description="Customer commitment and forecasting risks")
    product_liability_risks: Optional[str] = Field(None, description="Product liability and warranty risks")

class Item1ARiskFactors(BaseModel):
    risks_related_to_business: Optional[RisksRelatedToBusiness] = Field(None, description="Risks Related to our Business, Operations, Industry and Partners")

# Other Part I Items (simplified)
class Item1BUnresolvedStaffComments(BaseModel):
    content: Optional[str] = Field(None, description="None.")

class Item1CCybersecurity(BaseModel):
    risk_management_and_strategy: Optional[str] = Field(None, description="Risk Management and Strategy")
    governance: Optional[str] = Field(None, description="Governance")

class Item2Properties(BaseModel):
    properties_overview: Optional[str] = Field(None, description="Properties overview")

class Item3LegalProceedings(BaseModel):
    legal_proceedings_overview: Optional[str] = Field(None, description="Legal proceedings overview")

class Item4MineSafetyDisclosures(BaseModel):
    content: Optional[str] = Field(None, description="Not applicable.")

# PART I Model
class PartI(BaseModel):
    item_1_business: Optional[Item1Business] = Field(None, description="Item 1. Business")
    item_1a_risk_factors: Optional[Item1ARiskFactors] = Field(None, description="Item 1A. Risk Factors")
    item_1b_unresolved_staff_comments: Optional[Item1BUnresolvedStaffComments] = Field(None, description="Item 1B. Unresolved Staff Comments")
    item_1c_cybersecurity: Optional[Item1CCybersecurity] = Field(None, description="Item 1C. Cybersecurity")
    item_2_properties: Optional[Item2Properties] = Field(None, description="Item 2. Properties")
    item_3_legal_proceedings: Optional[Item3LegalProceedings] = Field(None, description="Item 3. Legal Proceedings")
    item_4_mine_safety_disclosures: Optional[Item4MineSafetyDisclosures] = Field(None, description="Item 4. Mine Safety Disclosures")

# PART II Models - Financial Statements
class ConsolidatedStatementsOfIncome(BaseModel):
    revenue: Optional[str] = Field(None, description="Revenue")
    cost_of_sales: Optional[str] = Field(None, description="Cost of sales")
    gross_margin: Optional[str] = Field(None, description="Gross margin")
    research_and_development: Optional[str] = Field(None, description="Research and development")
    selling_marketing_general_administrative: Optional[str] = Field(None, description="Selling, marketing, general and administrative")
    amortization_of_intangibles: Optional[str] = Field(None, description="Amortization of intangibles")
    special_charges_net: Optional[str] = Field(None, description="Special charges, net")
    total_operating_expenses: Optional[str] = Field(None, description="Total operating expenses")
    operating_income: Optional[str] = Field(None, description="Operating income")
    interest_expense: Optional[str] = Field(None, description="Interest expense")
    interest_income: Optional[str] = Field(None, description="Interest income")
    other_net: Optional[str] = Field(None, description="Other, net")
    total_nonoperating_expense: Optional[str] = Field(None, description="Total nonoperating expense (income)")
    income_before_income_taxes: Optional[str] = Field(None, description="Income before income taxes")
    provision_for_income_taxes: Optional[str] = Field(None, description="Provision for income taxes")
    net_income: Optional[str] = Field(None, description="Net income")
    shares_basic: Optional[str] = Field(None, description="Shares used to compute earnings per common share — basic")
    shares_diluted: Optional[str] = Field(None, description="Shares used to compute earnings per common share — diluted")
    basic_earnings_per_share: Optional[str] = Field(None, description="Basic earnings per common share")
    diluted_earnings_per_share: Optional[str] = Field(None, description="Diluted earnings per common share")

class ConsolidatedBalanceSheets(BaseModel):
    cash_and_cash_equivalents: Optional[str] = Field(None, description="Cash and cash equivalents")
    short_term_investments: Optional[str] = Field(None, description="Short-term investments")
    accounts_receivable_net: Optional[str] = Field(None, description="Accounts receivable less allowances")
    inventories: Optional[str] = Field(None, description="Inventories")
    prepaid_expenses_other_current_assets: Optional[str] = Field(None, description="Prepaid expenses and other current assets")
    total_current_assets: Optional[str] = Field(None, description="Total current assets")
    net_property_plant_equipment: Optional[str] = Field(None, description="Net property, plant and equipment")
    goodwill: Optional[str] = Field(None, description="Goodwill")
    intangible_assets_net: Optional[str] = Field(None, description="Intangible assets, net")
    deferred_tax_assets: Optional[str] = Field(None, description="Deferred tax assets")
    other_assets: Optional[str] = Field(None, description="Other assets")
    total_non_current_assets: Optional[str] = Field(None, description="Total non-current assets")
    total_assets: Optional[str] = Field(None, description="TOTAL ASSETS")
    accounts_payable: Optional[str] = Field(None, description="Accounts payable")
    income_taxes_payable_current: Optional[str] = Field(None, description="Income taxes payable")
    debt_current: Optional[str] = Field(None, description="Debt, current")
    commercial_paper_notes: Optional[str] = Field(None, description="Commercial paper notes")
    accrued_liabilities: Optional[str] = Field(None, description="Accrued liabilities")
    total_current_liabilities: Optional[str] = Field(None, description="Total current liabilities")
    long_term_debt: Optional[str] = Field(None, description="Long-term debt")
    deferred_income_taxes: Optional[str] = Field(None, description="Deferred income taxes")
    income_taxes_payable_non_current: Optional[str] = Field(None, description="Income taxes payable")
    other_non_current_liabilities: Optional[str] = Field(None, description="Other non-current liabilities")
    total_non_current_liabilities: Optional[str] = Field(None, description="Total non-current liabilities")
    preferred_stock: Optional[str] = Field(None, description="Preferred stock")
    common_stock: Optional[str] = Field(None, description="Common stock")
    capital_in_excess_of_par_value: Optional[str] = Field(None, description="Capital in excess of par value")
    retained_earnings: Optional[str] = Field(None, description="Retained earnings")
    accumulated_other_comprehensive_loss: Optional[str] = Field(None, description="Accumulated other comprehensive loss")
    total_shareholders_equity: Optional[str] = Field(None, description="Total shareholders' equity")
    total_liabilities_and_shareholders_equity: Optional[str] = Field(None, description="TOTAL LIABILITIES AND SHAREHOLDERS' EQUITY")

class ConsolidatedStatementsOfCashFlows(BaseModel):
    net_income_operating: Optional[str] = Field(None, description="Net income")
    depreciation: Optional[str] = Field(None, description="Depreciation")
    amortization_of_intangibles_cash: Optional[str] = Field(None, description="Amortization of intangibles")
    stock_based_compensation_expense: Optional[str] = Field(None, description="Stock-based compensation expense")
    deferred_income_taxes_cash: Optional[str] = Field(None, description="Deferred income taxes")
    accounts_receivable_change: Optional[str] = Field(None, description="Accounts receivable")
    inventories_change: Optional[str] = Field(None, description="Inventories")
    accounts_payable_change: Optional[str] = Field(None, description="Accounts payable and accrued liabilities")
    net_cash_provided_by_operating_activities: Optional[str] = Field(None, description="Net cash provided by operating activities")
    purchases_short_term_investments: Optional[str] = Field(None, description="Purchases of short-term investments")
    additions_property_plant_equipment: Optional[str] = Field(None, description="Additions to property, plant and equipment, net")
    net_cash_used_for_investing_activities: Optional[str] = Field(None, description="Net cash used for investing activities")
    proceeds_from_debt: Optional[str] = Field(None, description="Proceeds from debt")
    debt_repayments: Optional[str] = Field(None, description="Debt repayments")
    dividend_payments: Optional[str] = Field(None, description="Dividend payments to shareholders")
    repurchase_common_stock: Optional[str] = Field(None, description="Repurchase of common stock")
    net_cash_used_for_financing_activities: Optional[str] = Field(None, description="Net cash used for financing activities")
    net_change_cash: Optional[str] = Field(None, description="Net increase (decrease) in cash and cash equivalents")
    cash_beginning_year: Optional[str] = Field(None, description="Cash and cash equivalents at beginning of year")
    cash_end_year: Optional[str] = Field(None, description="Cash and cash equivalents at end of year")

class Item8FinancialStatements(BaseModel):
    consolidated_statements_of_income: Optional[ConsolidatedStatementsOfIncome] = Field(None, description="Consolidated Statements of Income")
    consolidated_balance_sheets: Optional[ConsolidatedBalanceSheets] = Field(None, description="Consolidated Balance Sheets")
    consolidated_statements_cash_flows: Optional[ConsolidatedStatementsOfCashFlows] = Field(None, description="Consolidated Statements of Cash Flows")

# Other Part II Items (simplified)
class Item5MarketForRegistrantsCommonEquity(BaseModel):
    trading_information: Optional[str] = Field(None, description="Common stock trading information")

class Item7ManagementDiscussionAndAnalysis(BaseModel):
    results_of_operations: Optional[str] = Field(None, description="Results of Operations overview")

class Item9AControlsProcedures(BaseModel):
    evaluation_disclosure_controls: Optional[str] = Field(None, description="Evaluation of Disclosure Controls and Procedures")

# PART II Model
class PartII(BaseModel):
    item_5_market_for_registrants_common_equity: Optional[Item5MarketForRegistrantsCommonEquity] = Field(None, description="Item 5. Market for Registrant's Common Equity")
    item_7_management_discussion_analysis: Optional[Item7ManagementDiscussionAndAnalysis] = Field(None, description="Item 7. Management's Discussion and Analysis")
    item_8_financial_statements: Optional[Item8FinancialStatements] = Field(None, description="Item 8. Financial Statements and Supplementary Data")
    item_9a_controls_procedures: Optional[Item9AControlsProcedures] = Field(None, description="Item 9A. Controls and Procedures")

# PART III and IV (simplified)
class PartIII(BaseModel):
    proxy_statement_reference: Optional[str] = Field(None, description="Items 10-14 incorporated by reference from proxy statement")

class PartIV(BaseModel):
    exhibits_and_schedules: Optional[str] = Field(None, description="Exhibits and Financial Statement Schedules")

# Signatures
class Signatures(BaseModel):
    signature_entries: Optional[str] = Field(None, description="Signature entries")

# Top-level Form 10-K Model
class Form10K(BaseModel):
    cover_page: Optional[CoverPage] = Field(None, description="Cover page")
    table_of_contents: Optional[TableOfContents] = Field(None, description="Table of Contents")
    note_about_forward_looking_statements: Optional[NoteAboutForwardLookingStatements] = Field(None, description="Note about Forward-Looking Statements")
    part_i: Optional[PartI] = Field(None, description="PART I")
    part_ii: Optional[PartII] = Field(None, description="PART II")
    part_iii: Optional[PartIII] = Field(None, description="PART III")
    part_iv: Optional[PartIV] = Field(None, description="PART IV")
    signatures: Optional[Signatures] = Field(None, description="Signatures")

# ============================================================================
# CREWAI + DOCLING INTEGRATION
# ============================================================================

class Form10KParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.content_source = CrewDoclingSource(file_paths=[pdf_path])
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        
    def _create_agents(self):
        return {
            'cover_page': Agent(
                role="Cover Page Extractor",
                goal="Extract cover page information from 10-K forms",
                backstory="You are an expert at extracting structured data from SEC filing cover pages. You extract company info, securities details, filing information, and format it as JSON matching the CoverPage Pydantic model structure.",
                verbose=True
            ),
            
            'business_section': Agent(
                role="Business Section Analyzer", 
                goal="Extract Item 1 Business section content",
                backstory="You specialize in parsing business descriptions, company overview, products, markets, competition from 10-K filings. You structure the output to match the Item1Business Pydantic model exactly.",
                verbose=True
            ),
            
            'financial_statements': Agent(
                role="Financial Data Extractor",
                goal="Extract financial statement data",
                backstory="You extract consolidated financial statements, income statements, balance sheets, cash flows. You preserve numerical accuracy and format output to match Item8FinancialStatements model structure.",
                verbose=True
            ),
            
            'orchestrator': Agent(
                role="10-K Form Orchestrator",
                goal="Combine all sections into complete Form 10-K structure",
                backstory="You coordinate all extractions and ensure the final JSON matches the complete Form10K Pydantic model structure with proper nesting and field names.",
                verbose=True
            )
        }
    
    def _create_tasks(self):
        return {
            'cover_page': Task(
                description="""
                Extract cover page information from the 10-K filing and return as JSON matching this exact structure:
                
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
                
                Use the exact field names shown above. Set fields to null if not found.
                """,
                agent=self.agents['cover_page'],
                expected_output="JSON object matching CoverPage model structure"
            ),
            
            'business_section': Task(
                description="""
                Extract Item 1. Business section and return as JSON matching this structure:
                
                {
                    "company_overview_strategy_and_mission": {
                        "company_description": "extracted company overview text",
                        "intelligent_edge_focus": "extracted intelligent edge content",
                        "key_priorities": "extracted key priorities"
                    },
                    "products": {
                        "semiconductor_overview": "extracted semiconductor overview",
                        "analog_and_mixed_signal": "extracted analog/mixed signal content",
                        "power_management_and_reference": "extracted power management content", 
                        "amplifiers_rf_and_microwave": "extracted amplifiers content"
                    },
                    "markets": {
                        "end_market_breakdown": {
                            "industrial_percent_2024": "46%",
                            "automotive_percent_2024": "30%",
                            "communications_percent_2024": "11%",
                            "consumer_percent_2024": "13%"
                        }
                    }
                }
                
                Extract the actual text content for each field. Use exact field names.
                """,
                agent=self.agents['business_section'],
                expected_output="JSON object matching Item1Business model structure"
            ),
            
            'financial_statements': Task(
                description="""
                Extract key financial data from Item 8 and return as JSON:
                
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
                
                Focus on the most recent year's data. Preserve exact numbers with currency symbols and commas.
                """,
                agent=self.agents['financial_statements'], 
                expected_output="JSON object with financial statements data"
            ),
            
            'combine_sections': Task(
                description="""
                Combine all extracted sections into a complete Form 10-K JSON structure:
                
                {
                    "cover_page": {cover_page_data},
                    "part_i": {
                        "item_1_business": {business_section_data}
                    },
                    "part_ii": {
                        "item_8_financial_statements": {financial_data}
                    }
                }
                
                Use the exact structure and field names to match the Form10K Pydantic model.
                """,
                agent=self.agents['orchestrator'],
                expected_output="Complete JSON matching Form10K model structure",
                context=['cover_page', 'business_section', 'financial_statements']
            )
        }
    
    def parse(self) -> Optional[Form10K]:
        """Parse the 10-K PDF and return populated Pydantic model"""
        try:
            # Create crew with all agents and tasks
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=list(self.tasks.values()),
                knowledge_sources=[self.content_source],
                verbose=True
            )
            
            # Execute parsing
            print("Starting 10-K parsing with CrewAI + Docling...")
            result = crew.kickoff()
            
            # Parse JSON result
            print("Parsing result to JSON...")
            parsed_data = json.loads(result.raw)
            
            # Validate and create Pydantic model
            print("Creating Pydantic model...")
            form_10k = Form10K(**parsed_data)
            
            print("✅ Successfully parsed 10-K to Pydantic model!")
            return form_10k
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw result: {result.raw}")
            return None
        except Exception as e:
            print(f"❌ Error parsing 10-K: {e}")
            return None
    
    def parse_section(self, section_name: str):
        """Parse a specific section only"""
        if section_name not in self.tasks:
            raise ValueError(f"Section '{section_name}' not found. Available: {list(self.tasks.keys())}")
        
        crew = Crew(
            agents=[self.agents[section_name]],
            tasks=[self.tasks[section_name]],
            knowledge_sources=[self.content_source],
            verbose=True
        )
        
        return crew.kickoff()

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def main():
    """Example usage of the 10-K parser"""
    
    # Initialize parser with your PDF path
    parser = Form10KParser("NASDAQ_ADI_2024.pdf")  # Update this path
    
    # Option 1: Parse entire 10-K
    parsed_10k = parser.parse()
    
    if parsed_10k:
        # Access structured data through Pydantic model
        print(f"Company: {parsed_10k.cover_page.registrant_name}")
        print(f"Fiscal Year: {parsed_10k.cover_page.fiscal_year_ended}")
        
        if parsed_10k.part_i and parsed_10k.part_i.item_1_business:
            business = parsed_10k.part_i.item_1_business
            if business.company_overview_strategy_and_mission:
                print(f"Business Overview: {business.company_overview_strategy_and_mission.company_description}")
        
        if parsed_10k.part_ii and parsed_10k.part_ii.item_8_financial_statements:
            financials = parsed_10k.part_ii.item_8_financial_statements
            if financials.consolidated_statements_of_income:
                print(f"Revenue: {financials.consolidated_statements_of_income.revenue}")
                print(f"Net Income: {financials.consolidated_statements_of_income.net_income}")
        
        # Save to JSON file
        with open("parsed_10k.json", "w") as f:
            json.dump(parsed_10k.model_dump(), f, indent=2)
            
        print("✅ Saved parsed 10-K to parsed_10k.json")
        
    else:
        print("❌ Failed to parse 10-K")
    
    # Option 2: Parse specific section for testing
    print("\n" + "="*50)
    print("Testing individual section parsing...")
    
    try:
        cover_result = parser.parse_section('cover_page')
        print(f"Cover page result: {cover_result.raw}")
    except Exception as e:
        print(f"Error parsing cover page: {e}")

if __name__ == "__main__":
    # Install required packages first:
    # pip install crewai docling pydantic
    
    main()