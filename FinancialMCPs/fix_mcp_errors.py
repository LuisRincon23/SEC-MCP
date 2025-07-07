#\!/usr/bin/env python3
"""
Fix specific errors in the MCPs that are preventing them from connecting
"""

import re
from pathlib import Path


def fix_operation_error(content: str) -> str:
    """Fix the undefined 'operation' variable error"""
    
    # Find pattern where we incorrectly added {operation}
    pattern = r"Failed to {operation}"
    
    if pattern in content:
        # Replace with the actual function name based on context
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if '{operation}' in line and 'Failed to' in line:
                # Look backwards to find the function name
                func_name = None
                for j in range(i-1, max(0, i-20), -1):
                    if 'async def ' in lines[j]:
                        match = re.search(r'async def (\w+)', lines[j])
                        if match:
                            func_name = match.group(1).replace('_', ' ')
                            break
                
                if func_name:
                    fixed_line = line.replace('{operation}', func_name)
                else:
                    # Generic fallback
                    fixed_line = line.replace('Failed to {operation}', 'Operation failed')
                
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    return content


def main():
    """Fix all MCP errors"""
    
    print("🔧 Fixing MCP Connection Errors")
    print("=" * 40)
    
    base_dir = Path("/Users/LuisRincon/SEC-MCP/FinancialMCPs")
    
    # Fix SEC_SCRAPER_MCP specifically
    sec_main = base_dir / "SEC_SCRAPER_MCP" / "src" / "main.py"
    
    if sec_main.exists():
        print("Fixing SEC_SCRAPER_MCP...")
        content = sec_main.read_text()
        
        # Fix the operation error
        content = fix_operation_error(content)
        
        sec_main.write_text(content)
        print("  ✅ Fixed operation error")
    
    print("\n✅ MCPs fixed\!")
    print("\nThe 'Method not found' errors for resources/list and prompts/list are normal.")
    print("These methods are optional and not all MCPs implement them.")


if __name__ == "__main__":
    main()
EOF < /dev/null
