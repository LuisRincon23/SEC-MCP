#!/usr/bin/env python3
"""Fix session management issues in all MCP Python files"""

import os
import re
from pathlib import Path

def fix_session_issues(file_path):
    """Fix session management issues in a Python file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Fix 1: Remove cleanup() calls from finally blocks
    if 'finally:' in content and 'cleanup()' in content:
        # Find all finally blocks with cleanup
        pattern = r'finally:\s*await\s+(?:self\.)?(?:scraper\.)?cleanup\(\)'
        if re.search(pattern, content):
            content = re.sub(pattern, 'finally:\n            pass  # Session cleanup removed to maintain persistence', content)
            changes_made.append("Removed cleanup() from finally blocks")
    
    # Fix 2: Update session check to include closed state
    old_check = 'if not self.session:'
    new_check = 'if not self.session or self.session.closed:'
    if old_check in content and new_check not in content:
        content = content.replace(old_check, new_check)
        changes_made.append("Updated session check to include closed state")
    
    # Fix 3: Remove automatic cleanup in tool calls
    cleanup_pattern = r'await\s+scraper\.cleanup\(\)'
    if re.search(cleanup_pattern, content):
        content = re.sub(cleanup_pattern, '# await scraper.cleanup()  # Removed to maintain session', content)
        changes_made.append("Commented out cleanup calls")
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path, changes_made
    
    return None, []

def main():
    base_dir = Path("/Users/LuisRincon/SEC-MCP/FinancialMCPs")
    
    print("🔧 Fixing session management issues in MCP files...")
    print("=" * 50)
    
    fixed_files = []
    
    # Find all main.py files
    for mcp_dir in base_dir.iterdir():
        if mcp_dir.is_dir() and not mcp_dir.name.startswith('.'):
            main_file = mcp_dir / "src" / "main.py"
            if main_file.exists():
                file_path, changes = fix_session_issues(main_file)
                if file_path:
                    fixed_files.append((file_path, changes))
                    print(f"✓ Fixed {mcp_dir.name}:")
                    for change in changes:
                        print(f"  - {change}")
                else:
                    print(f"✓ {mcp_dir.name}: No issues found")
    
    print("\n" + "=" * 50)
    print(f"Summary: Fixed {len(fixed_files)} files")
    
    if fixed_files:
        print("\nFixed files:")
        for file_path, _ in fixed_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()