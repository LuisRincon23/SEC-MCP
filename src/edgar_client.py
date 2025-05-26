import asyncio
import aiohttp
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
import logging

class EdgarClient:
    """Async client for SEC EDGAR API"""
    
    BASE_URL = "https://data.sec.gov"
    COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    COMPANY_TICKERS_EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
    
    def __init__(self, user_agent: str = "Edgar MCP Tool contact@example.com"):
        self.user_agent = user_agent
        self.session = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.user_agent},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make async HTTP request with error handling"""
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"API request failed: {response.status} - {url}")
                    response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            raise
            
    async def get_company_submissions(self, cik: str) -> Dict:
        """Get company submissions by CIK"""
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"
        return await self._make_request(url)
        
    async def get_company_facts(self, cik: str) -> Dict:
        """Get all company facts by CIK"""
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"
        return await self._make_request(url)
        
    async def get_company_concept(self, cik: str, taxonomy: str, tag: str) -> Dict:
        """Get specific company concept data"""
        cik_padded = str(cik).zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyconcept/CIK{cik_padded}/{taxonomy}/{tag}.json"
        return await self._make_request(url)
        
    async def get_xbrl_frames(self, taxonomy: str, tag: str, unit: str, year: int, quarter: Optional[int] = None) -> Dict:
        """Get XBRL frames data"""
        period = f"CY{year}"
        if quarter:
            period += f"Q{quarter}I"
        url = f"{self.BASE_URL}/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json"
        return await self._make_request(url)
        
    async def search_companies(self, query: str, size: int = 20) -> Dict:
        """Search for companies by name or ticker using SEC official lookup files"""
        try:
            # First, try to get the company_tickers_exchange.json for more comprehensive data
            company_data = await self._make_request(self.COMPANY_TICKERS_EXCHANGE_URL)
            
            # Convert to list format for easier searching
            companies = []
            if isinstance(company_data, dict) and "data" in company_data:
                # Handle the data structure with numbered keys
                for entry in company_data["data"]:
                    if len(entry) >= 4:  # Ensure we have enough fields
                        companies.append({
                            "cik": str(entry[0]).zfill(10),
                            "name": entry[1],
                            "ticker": entry[2] if entry[2] else "",
                            "exchange": entry[3] if len(entry) > 3 else ""
                        })
            else:
                # If the exchange file doesn't work, fall back to basic tickers file
                basic_data = await self._make_request(self.COMPANY_TICKERS_URL)
                for key, company in basic_data.items():
                    if key.isdigit():  # Skip metadata fields
                        companies.append({
                            "cik": str(company.get("cik_str", "")).zfill(10),
                            "name": company.get("title", ""),
                            "ticker": company.get("ticker", ""),
                            "exchange": ""
                        })
            
            # Search through companies
            query_lower = query.lower()
            matches = []
            
            for company in companies:
                # Search by ticker (exact match) or company name (partial match)
                if (company["ticker"].lower() == query_lower or 
                    query_lower in company["name"].lower() or
                    company["ticker"].lower().startswith(query_lower)):
                    matches.append(company)
                    
                if len(matches) >= size:
                    break
            
            # Return in the expected format
            return {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "entity": match["name"],
                                "cik": match["cik"],
                                "tickers": [match["ticker"]] if match["ticker"] else [],
                                "exchange": match.get("exchange", "")
                            }
                        } for match in matches
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error searching companies: {str(e)}")
            # Return empty result on error
            return {"hits": {"hits": []}}
        
    async def download_filing(self, cik: str, accession_number: str, filename: str = None) -> bytes:
        """Download a specific filing document"""
        # Ensure CIK is properly formatted (10 digits with leading zeros)
        formatted_cik = str(cik).zfill(10)
        
        # Remove dashes from accession number for directory path
        clean_accession = accession_number.replace("-", "")
        
        if filename:
            # Custom filename provided
            url = f"https://www.sec.gov/Archives/edgar/data/{formatted_cik}/{clean_accession}/{filename}"
        else:
            # Default to main filing document (.txt format)
            url = f"https://www.sec.gov/Archives/edgar/data/{formatted_cik}/{clean_accession}/{accession_number}.txt"
            
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                response.raise_for_status()
                
    def format_cik(self, cik: Union[str, int]) -> str:
        """Format CIK to 10-digit padded string"""
        return str(cik).zfill(10)
        
    def parse_filing_date(self, date_str: str) -> datetime:
        """Parse filing date string to datetime"""
        return datetime.strptime(date_str, "%Y-%m-%d")
