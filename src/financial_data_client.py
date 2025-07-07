"""Financial data client for extracting structured financial statements from SEC filings."""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class FinancialDataClient:
    """Client for parsing and extracting financial statement data from SEC filings."""
    
    def __init__(self, edgar_client):
        self.edgar_client = edgar_client
        
    async def get_income_statement(self, cik: str, period: str = "annual", years: int = 3) -> Dict[str, Any]:
        """Extract income statement data from company facts."""
        try:
            # Get company facts
            facts = await self.edgar_client.get_company_facts(cik)
            company_name = facts.get("entityName", "Unknown Company")
            
            # Extract income statement items
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            
            income_items = {
                "revenues": self._extract_concept(us_gaap, ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]),
                "cost_of_revenue": self._extract_concept(us_gaap, ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"]),
                "gross_profit": self._extract_concept(us_gaap, ["GrossProfit"]),
                "operating_expenses": self._extract_concept(us_gaap, ["OperatingExpenses"]),
                "research_development": self._extract_concept(us_gaap, ["ResearchAndDevelopmentExpense"]),
                "selling_general_admin": self._extract_concept(us_gaap, ["SellingGeneralAndAdministrativeExpense"]),
                "operating_income": self._extract_concept(us_gaap, ["OperatingIncomeLoss"]),
                "interest_expense": self._extract_concept(us_gaap, ["InterestExpense"]),
                "income_before_tax": self._extract_concept(us_gaap, ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"]),
                "income_tax_expense": self._extract_concept(us_gaap, ["IncomeTaxExpenseBenefit"]),
                "net_income": self._extract_concept(us_gaap, ["NetIncomeLoss"]),
                "earnings_per_share_basic": self._extract_concept(us_gaap, ["EarningsPerShareBasic"]),
                "earnings_per_share_diluted": self._extract_concept(us_gaap, ["EarningsPerShareDiluted"]),
                "shares_outstanding_basic": self._extract_concept(us_gaap, ["WeightedAverageNumberOfSharesOutstandingBasic"]),
                "shares_outstanding_diluted": self._extract_concept(us_gaap, ["WeightedAverageNumberOfDilutedSharesOutstanding"])
            }
            
            # Filter by period type and years
            filtered_data = self._filter_by_period(income_items, period, years)
            
            return {
                "company_name": company_name,
                "cik": cik,
                "statement_type": "income_statement",
                "period": period,
                "data": filtered_data
            }
            
        except Exception as e:
            raise Exception(f"Error extracting income statement: {str(e)}")
    
    async def get_balance_sheet(self, cik: str, period: str = "annual", years: int = 3) -> Dict[str, Any]:
        """Extract balance sheet data from company facts."""
        try:
            # Get company facts
            facts = await self.edgar_client.get_company_facts(cik)
            company_name = facts.get("entityName", "Unknown Company")
            
            # Extract balance sheet items
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            
            balance_items = {
                # Assets
                "cash_and_equivalents": self._extract_concept(us_gaap, ["CashAndCashEquivalentsAtCarryingValue", "Cash"]),
                "marketable_securities": self._extract_concept(us_gaap, ["MarketableSecuritiesCurrent"]),
                "accounts_receivable": self._extract_concept(us_gaap, ["AccountsReceivableNetCurrent"]),
                "inventory": self._extract_concept(us_gaap, ["InventoryNet"]),
                "current_assets": self._extract_concept(us_gaap, ["AssetsCurrent"]),
                "property_plant_equipment": self._extract_concept(us_gaap, ["PropertyPlantAndEquipmentNet"]),
                "goodwill": self._extract_concept(us_gaap, ["Goodwill"]),
                "intangible_assets": self._extract_concept(us_gaap, ["IntangibleAssetsNetExcludingGoodwill"]),
                "total_assets": self._extract_concept(us_gaap, ["Assets"]),
                
                # Liabilities
                "accounts_payable": self._extract_concept(us_gaap, ["AccountsPayableCurrent"]),
                "short_term_debt": self._extract_concept(us_gaap, ["ShortTermBorrowings", "DebtCurrent"]),
                "current_liabilities": self._extract_concept(us_gaap, ["LiabilitiesCurrent"]),
                "long_term_debt": self._extract_concept(us_gaap, ["LongTermDebtNoncurrent", "LongTermDebt"]),
                "total_liabilities": self._extract_concept(us_gaap, ["Liabilities"]),
                
                # Equity
                "common_stock": self._extract_concept(us_gaap, ["CommonStockValue"]),
                "retained_earnings": self._extract_concept(us_gaap, ["RetainedEarningsAccumulatedDeficit"]),
                "treasury_stock": self._extract_concept(us_gaap, ["TreasuryStockValue"]),
                "total_equity": self._extract_concept(us_gaap, ["StockholdersEquity"])
            }
            
            # Filter by period type and years
            filtered_data = self._filter_by_period(balance_items, period, years)
            
            return {
                "company_name": company_name,
                "cik": cik,
                "statement_type": "balance_sheet",
                "period": period,
                "data": filtered_data
            }
            
        except Exception as e:
            raise Exception(f"Error extracting balance sheet: {str(e)}")
    
    async def get_cash_flow_statement(self, cik: str, period: str = "annual", years: int = 3) -> Dict[str, Any]:
        """Extract cash flow statement data from company facts."""
        try:
            # Get company facts
            facts = await self.edgar_client.get_company_facts(cik)
            company_name = facts.get("entityName", "Unknown Company")
            
            # Extract cash flow items
            us_gaap = facts.get("facts", {}).get("us-gaap", {})
            
            cash_flow_items = {
                # Operating Activities
                "net_income": self._extract_concept(us_gaap, ["NetIncomeLoss"]),
                "depreciation_amortization": self._extract_concept(us_gaap, ["DepreciationDepletionAndAmortization"]),
                "stock_based_compensation": self._extract_concept(us_gaap, ["ShareBasedCompensation"]),
                "change_in_working_capital": self._extract_concept(us_gaap, ["IncreaseDecreaseInOperatingCapital"]),
                "operating_cash_flow": self._extract_concept(us_gaap, ["NetCashProvidedByUsedInOperatingActivities"]),
                
                # Investing Activities
                "capital_expenditures": self._extract_concept(us_gaap, ["PaymentsToAcquirePropertyPlantAndEquipment"]),
                "acquisitions": self._extract_concept(us_gaap, ["PaymentsToAcquireBusinessesNetOfCashAcquired"]),
                "investment_purchases": self._extract_concept(us_gaap, ["PaymentsToAcquireInvestments"]),
                "investment_sales": self._extract_concept(us_gaap, ["ProceedsFromSaleMaturityAndCollectionsOfInvestments"]),
                "investing_cash_flow": self._extract_concept(us_gaap, ["NetCashProvidedByUsedInInvestingActivities"]),
                
                # Financing Activities
                "debt_issuance": self._extract_concept(us_gaap, ["ProceedsFromIssuanceOfDebt", "ProceedsFromIssuanceOfLongTermDebt"]),
                "debt_repayment": self._extract_concept(us_gaap, ["RepaymentsOfDebt", "RepaymentsOfLongTermDebt"]),
                "stock_issuance": self._extract_concept(us_gaap, ["ProceedsFromIssuanceOfCommonStock"]),
                "stock_repurchase": self._extract_concept(us_gaap, ["PaymentsForRepurchaseOfCommonStock"]),
                "dividends_paid": self._extract_concept(us_gaap, ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"]),
                "financing_cash_flow": self._extract_concept(us_gaap, ["NetCashProvidedByUsedInFinancingActivities"]),
                
                # Net Change
                "net_change_in_cash": self._extract_concept(us_gaap, ["CashAndCashEquivalentsPeriodIncreaseDecrease"]),
                "cash_beginning": self._extract_concept(us_gaap, ["CashAndCashEquivalentsAtCarryingValue"]),
                "cash_ending": self._extract_concept(us_gaap, ["CashAndCashEquivalentsAtCarryingValue"])
            }
            
            # Filter by period type and years
            filtered_data = self._filter_by_period(cash_flow_items, period, years)
            
            return {
                "company_name": company_name,
                "cik": cik,
                "statement_type": "cash_flow_statement",
                "period": period,
                "data": filtered_data
            }
            
        except Exception as e:
            raise Exception(f"Error extracting cash flow statement: {str(e)}")
    
    def _extract_concept(self, us_gaap: Dict, concept_names: List[str]) -> Optional[Dict]:
        """Extract the first available concept from a list of possible names."""
        for concept_name in concept_names:
            if concept_name in us_gaap:
                return us_gaap[concept_name]
        return None
    
    def _filter_by_period(self, data: Dict[str, Optional[Dict]], period: str, years: int) -> Dict[str, Any]:
        """Filter financial data by period type (annual/quarterly) and number of years."""
        filtered_result = {}
        
        for item_name, item_data in data.items():
            if not item_data:
                filtered_result[item_name] = None
                continue
                
            # Get the USD unit data (most common for financial statements)
            units = item_data.get("units", {})
            usd_data = units.get("USD", [])
            
            if not usd_data:
                # Try other currency units
                for unit, values in units.items():
                    if unit.endswith("USD") or unit == "shares":
                        usd_data = values
                        break
            
            if not usd_data:
                filtered_result[item_name] = None
                continue
            
            # Filter by period type
            filtered_values = []
            for value in usd_data:
                form = value.get("form", "")
                
                # Filter by form type
                if period == "annual" and form in ["10-K", "20-F", "40-F"]:
                    filtered_values.append(value)
                elif period == "quarterly" and form in ["10-Q"]:
                    filtered_values.append(value)
            
            # Sort by end date (most recent first)
            filtered_values.sort(key=lambda x: x.get("end", ""), reverse=True)
            
            # Limit to requested number of years
            if period == "annual":
                filtered_values = filtered_values[:years]
            else:  # quarterly
                filtered_values = filtered_values[:years * 4]
            
            # Format the data
            formatted_values = []
            for value in filtered_values:
                formatted_values.append({
                    "value": value.get("val"),
                    "end_date": value.get("end"),
                    "start_date": value.get("start"),
                    "form": value.get("form"),
                    "filed": value.get("filed"),
                    "accession": value.get("accn")
                })
            
            filtered_result[item_name] = {
                "description": item_data.get("description", item_name),
                "unit": "USD" if "USD" in units else list(units.keys())[0] if units else "unknown",
                "values": formatted_values
            }
        
        return filtered_result