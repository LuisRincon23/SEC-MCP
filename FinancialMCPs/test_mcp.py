#!/usr/bin/env python
"""Test script to verify MCP servers start correctly"""

import subprocess
import sys
import time
import signal
import os

def test_mcp_server(server_path, server_name):
    """Test if an MCP server starts correctly"""
    print(f"\nTesting {server_name}...")
    
    # Change to server directory
    original_dir = os.getcwd()
    os.chdir(server_path)
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "src/main.py", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization message
        init_message = '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "1.0", "capabilities": {}}, "id": 1}\n'
        process.stdin.write(init_message)
        process.stdin.flush()
        
        # Wait for response
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✓ {server_name} started successfully")
            # Terminate the process
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            # Process ended, check stderr
            stderr = process.stderr.read()
            print(f"✗ {server_name} failed to start")
            print(f"  Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ {server_name} error: {str(e)}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Test all MCP servers"""
    servers = [
        ("SEC_SCRAPER_MCP", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP"),
        ("NEWS_SENTIMENT_SCRAPER", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/NEWS_SENTIMENT_SCRAPER"),
        ("ANALYST_RATINGS_SCRAPER", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ANALYST_RATINGS_SCRAPER"),
        ("INSTITUTIONAL_SCRAPER", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INSTITUTIONAL_SCRAPER"),
        ("ALTERNATIVE_DATA_SCRAPER", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ALTERNATIVE_DATA_SCRAPER"),
        ("INDUSTRY_ASSUMPTIONS_ENGINE", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/INDUSTRY_ASSUMPTIONS_ENGINE"),
        ("ECONOMIC_DATA_COLLECTOR", "/Users/LuisRincon/SEC-MCP/FinancialMCPs/ECONOMIC_DATA_COLLECTOR"),
    ]
    
    results = []
    for name, path in servers:
        success = test_mcp_server(path, name)
        results.append((name, success))
    
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print("="*50)
    
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} servers passed")

if __name__ == "__main__":
    main()