#!/usr/bin/env python3
"""
Fix critical data extraction issues in Financial MCPs
- Updates User-Agents
- Implements data validation
- Adds error handling
- Updates outdated selectors
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional


def fix_user_agents(content: str, filename: str) -> Tuple[str, List[str]]:
    """Fix User-Agent issues"""
    changes_made = []
    
    # Fix SEC placeholder User-Agent
    if 'Your Company Name your.email@company.com' in content:
        content = content.replace(
            "'User-Agent': 'Your Company Name your.email@company.com'",
            "'User-Agent': 'FinancialMCP/1.0 (Personal Research Tool; Contact: research@example.com)'"
        )
        changes_made.append("Fixed SEC placeholder User-Agent")
    
    # Fix incomplete browser User-Agents
    incomplete_ua = "'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'"
    complete_ua = "'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'"
    
    if incomplete_ua in content:
        content = content.replace(incomplete_ua, complete_ua)
        changes_made.append("Updated incomplete browser User-Agent")
    
    return content, changes_made


def add_data_validation(content: str, filename: str) -> Tuple[str, List[str]]:
    """Add data validation to scrapers"""
    changes_made = []
    
    # Add validation helper if not present
    validation_helper = '''
    def validate_price(self, price_str: str) -> Optional[float]:
        """Validate and parse price data"""
        try:
            # Remove common formatting
            clean_price = re.sub(r'[$,]', '', str(price_str))
            price = float(clean_price)
            
            # Sanity checks
            if price <= 0 or price > 1000000:
                return None
            
            return price
        except:
            return None
    
    def validate_date(self, date_str: str) -> Optional[str]:
        """Validate date format"""
        try:
            # Try to parse various date formats
            from datetime import datetime
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%d-%b-%Y']:
                try:
                    datetime.strptime(date_str.strip(), fmt)
                    return date_str.strip()
                except:
                    continue
            return None
        except:
            return None
    
    def validate_percentage(self, pct_str: str) -> Optional[float]:
        """Validate percentage data"""
        try:
            # Remove % and convert
            clean_pct = re.sub(r'[%()]', '', str(pct_str))
            pct = float(clean_pct)
            
            # Sanity check
            if abs(pct) > 1000:  # More than 1000% change is suspicious
                return None
            
            return pct
        except:
            return None
'''
    
    # Add validation methods after class definition
    if 'class' in content and 'validate_price' not in content:
        # Find the __init__ method and add validation methods after it
        init_match = re.search(r'(def __init__.*?\n(?:.*?\n)*?)\n    def', content, re.MULTILINE)
        if init_match:
            insert_pos = init_match.end(1)
            content = content[:insert_pos] + validation_helper + content[insert_pos:]
            changes_made.append("Added data validation methods")
    
    return content, changes_made


def update_selectors(content: str, filename: str) -> Tuple[str, List[str]]:
    """Update outdated HTML selectors with more robust alternatives"""
    changes_made = []
    
    selector_updates = {
        # Finviz updates
        "'fullview-news-outer'": "'news-table'",
        "'fullview-ratings-outer'": "'ratings-outer'",
        "'snapshot-table2'": "'snapshot-table'",
        
        # Generic updates for robustness
        "soup.find('table', {'class': 'tableFile2'})": 
            "soup.find('table', {'class': re.compile('tableFile')}) or soup.find('table', {'summary': re.compile('Document')})",
        
        "soup.find('span', {'class': 'companyName'})":
            "soup.find('span', {'class': re.compile('companyName')}) or soup.find(text=re.compile('CIK#:'))",
        
        # Add fallback selectors
        "fin-streamer[data-field=\"regularMarketPrice\"]":
            "fin-streamer[data-field=\"regularMarketPrice\"], [data-symbol][data-field=\"regularMarketPrice\"], .Fw\\(b\\).Fz\\(36px\\)"
    }
    
    for old, new in selector_updates.items():
        if old in content:
            content = content.replace(old, new)
            changes_made.append(f"Updated selector: {old[:30]}...")
    
    return content, changes_made


def add_error_handling(content: str, filename: str) -> Tuple[str, List[str]]:
    """Improve error handling with retries and better messages"""
    changes_made = []
    
    # Add retry decorator if not present
    retry_decorator = '''import asyncio
from functools import wraps

def async_retry(max_attempts=3, delay=1):
    """Retry decorator for async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                    continue
            raise last_exception
        return wrapper
    return decorator

'''
    
    # Add retry decorator at the top of file if not present
    if 'async_retry' not in content and 'import asyncio' in content:
        # Find the last import statement
        import_match = list(re.finditer(r'^import.*\n|^from.*import.*\n', content, re.MULTILINE))
        if import_match:
            insert_pos = import_match[-1].end()
            content = content[:insert_pos] + "\n" + retry_decorator + content[insert_pos:]
            changes_made.append("Added retry decorator")
    
    # Improve error messages
    generic_errors = [
        (r"return \[{'error': f'Failed to.*?: {str\(e\)}'}\]",
         "return [{'error': f'Failed to {operation}: {type(e).__name__}: {str(e)}', 'retry_possible': True}]"),
        
        (r"except Exception as e:\s*return \[{'error':",
         "except aiohttp.ClientError as e:\n            return [{'error': f'Network error: {str(e)}', 'retry_possible': True}]\n        except Exception as e:\n            return [{'error':")
    ]
    
    for pattern, replacement in generic_errors:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made.append("Improved error handling")
    
    return content, changes_made


def add_rate_limiting(content: str, filename: str) -> Tuple[str, List[str]]:
    """Add rate limiting to prevent bans"""
    changes_made = []
    
    rate_limiter = '''
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = {}
        self.min_delay = 1.0  # Minimum 1 second between requests to same domain
'''
    
    rate_limit_method = '''
    async def rate_limit(self, url: str):
        """Implement rate limiting per domain"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.min_delay:
                await asyncio.sleep(self.min_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
'''
    
    # Add rate limiting if not present
    if 'rate_limit' not in content and '__init__' in content:
        # Update __init__ to include rate limiting
        init_pattern = r'(def __init__\(self\):.*?self\.session.*?\n)'
        match = re.search(init_pattern, content, re.DOTALL)
        if match:
            old_init = match.group(1)
            new_init = old_init.rstrip() + '\n        self.last_request_time = {}\n        self.min_delay = 1.0  # Rate limiting\n'
            content = content.replace(old_init, new_init)
            
            # Add rate_limit method after __init__
            content = content.replace(new_init, new_init + rate_limit_method)
            
            # Add time import if needed
            if 'import time' not in content:
                content = 'import time\n' + content
            
            changes_made.append("Added rate limiting")
    
    return content, changes_made


def process_file(filepath: Path) -> List[str]:
    """Process a single Python file"""
    print(f"\nProcessing {filepath.name}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    all_changes = []
    
    # Apply fixes
    fixes = [
        fix_user_agents,
        add_data_validation,
        update_selectors,
        add_error_handling,
        add_rate_limiting
    ]
    
    for fix_func in fixes:
        content, changes = fix_func(content, filepath.name)
        all_changes.extend(changes)
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Applied {len(all_changes)} fixes:")
        for change in all_changes:
            print(f"   - {change}")
    else:
        print("✓ No changes needed")
    
    return all_changes


def main():
    """Fix critical issues in all MCP scrapers"""
    base_dir = Path("/Users/LuisRincon/SEC-MCP/FinancialMCPs")
    
    print("🔧 Fixing Critical Data Extraction Issues")
    print("=" * 50)
    
    total_changes = 0
    
    # Process each MCP's main.py
    mcps = [
        "SEC_SCRAPER_MCP",
        "NEWS_SENTIMENT_SCRAPER", 
        "ANALYST_RATINGS_SCRAPER",
        "INSTITUTIONAL_SCRAPER",
        "ALTERNATIVE_DATA_SCRAPER",
        "INDUSTRY_ASSUMPTIONS_ENGINE",
        "ECONOMIC_DATA_COLLECTOR",
        "RESEARCH_ADMINISTRATOR"
    ]
    
    for mcp in mcps:
        main_file = base_dir / mcp / "src" / "main.py"
        if main_file.exists():
            changes = process_file(main_file)
            total_changes += len(changes)
        else:
            print(f"\n❌ {mcp}/src/main.py not found")
    
    print("\n" + "=" * 50)
    print(f"✅ Total fixes applied: {total_changes}")
    print("\n⚠️  IMPORTANT: The MCPs still need:")
    print("1. Proper API keys for services that require them")
    print("2. More sophisticated sentiment analysis (consider using NLP libraries)")
    print("3. Fallback data sources when primary sources fail")
    print("4. Comprehensive testing with real data")
    print("\nRestart Claude Desktop to apply these changes!")


if __name__ == "__main__":
    main()