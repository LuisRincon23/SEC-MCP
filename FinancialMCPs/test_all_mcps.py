#!/usr/bin/env python3
"""
Comprehensive MCP Testing Framework
Tests all Financial MCPs for functionality, accuracy, and performance
"""

import asyncio
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time


class MCPTester:
    """Test all Financial MCPs systematically"""
    
    def __init__(self):
        self.results = {}
        self.mcps = {
            'SEC': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh',
                'tests': [
                    ('scrape_10k_financials', {'ticker': 'AAPL'}),
                    ('parse_xbrl_data', {'ticker': 'MSFT'}),
                    ('get_current_price', {'ticker': 'GOOGL'})
                ]
            },
            'NEWS-SENTIMENT': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/NEWS_SENTIMENT_SCRAPER/start-mcp.sh',
                'tests': [
                    ('analyze_news_sentiment', {'ticker': 'TSLA'}),
                    ('get_aggregate_sentiment', {'ticker': 'NVDA'}),
                    ('analyze_earnings_sentiment', {'ticker': 'AAPL'})
                ]
            },
            'X-SENTIMENT': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/X_SENTIMENT_MCP/start-mcp.sh',
                'tests': [
                    ('analyze_ticker_sentiment', {'ticker': 'BTC'}),
                    ('compare_tickers_sentiment', {'tickers': ['AAPL', 'MSFT']}),
                    ('sentiment_alerts', {'ticker': 'GME'})
                ]
            },
            'ANALYST-RATINGS': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/ANALYST_RATINGS_SCRAPER/start-mcp.sh',
                'tests': [
                    ('get_consensus_rating', {'ticker': 'AAPL'}),
                    ('get_price_targets', {'ticker': 'TSLA'}),
                    ('track_rating_changes', {'ticker': 'NVDA', 'days': 30})
                ]
            },
            'INSTITUTIONAL': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/INSTITUTIONAL_SCRAPER/start-mcp.sh',
                'tests': [
                    ('get_institutional_holdings', {'ticker': 'AAPL'}),
                    ('track_ownership_changes', {'ticker': 'MSFT'}),
                    ('get_top_holders', {'ticker': 'GOOGL'})
                ]
            },
            'ALTERNATIVE-DATA': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/ALTERNATIVE_DATA_SCRAPER/start-mcp.sh',
                'tests': [
                    ('analyze_hiring_trends', {'company': 'Amazon'}),
                    ('get_reddit_sentiment', {'query': 'TSLA stock'}),
                    ('track_web_traffic', {'domain': 'tesla.com'})
                ]
            },
            'INDUSTRY-ASSUMPTIONS': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/INDUSTRY_ASSUMPTIONS_ENGINE/start-mcp.sh',
                'tests': [
                    ('calculate_industry_wacc', {'ticker': 'AAPL'}),
                    ('get_sector_assumptions', {'sector': 'Technology'}),
                    ('benchmark_metrics', {'ticker': 'MSFT'})
                ]
            },
            'ECONOMIC-DATA': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/ECONOMIC_DATA_COLLECTOR/start-mcp.sh',
                'tests': [
                    ('get_economic_indicators', {}),
                    ('analyze_market_regime', {}),
                    ('get_fed_data', {})
                ]
            },
            'RESEARCH-ADMIN': {
                'path': '/Users/LuisRincon/SEC-MCP/FinancialMCPs/RESEARCH_ADMINISTRATOR/start-mcp.sh',
                'tests': [
                    ('create_research_summary', {'ticker': 'AAPL'}),
                    ('generate_investment_thesis', {'ticker': 'TSLA'}),
                    ('compile_comprehensive_report', {'ticker': 'NVDA'})
                ]
            }
        }
    
    async def test_mcp_connection(self, name: str, path: str) -> Dict[str, Any]:
        """Test if MCP can be connected to"""
        print(f"\n🔌 Testing connection to {name}...")
        
        # Test initialization
        init_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0", 
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        })
        
        try:
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send initialization
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=init_request.encode() + b'\n'),
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            # Parse response
            if stdout:
                try:
                    # Find JSON response
                    for line in stdout.decode().split('\n'):
                        if line.strip() and '{' in line:
                            response = json.loads(line.strip())
                            if 'result' in response:
                                return {
                                    'status': 'connected',
                                    'response_time': response_time,
                                    'server_info': response['result'].get('serverInfo', {})
                                }
                except json.JSONDecodeError:
                    pass
            
            if stderr:
                return {
                    'status': 'error',
                    'error': stderr.decode()[:200]
                }
            
            return {
                'status': 'no_response',
                'stdout': stdout.decode()[:200] if stdout else None
            }
            
        except asyncio.TimeoutError:
            return {'status': 'timeout'}
        except Exception as e:
            return {'status': 'exception', 'error': str(e)}
    
    async def test_mcp_tool(self, name: str, path: str, tool: str, 
                           params: Dict) -> Dict[str, Any]:
        """Test a specific MCP tool"""
        print(f"  🔧 Testing {name}.{tool}...")
        
        # Create tool call request
        request = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": params
            },
            "id": 2
        })
        
        try:
            start_time = time.time()
            
            # Initialize first
            init_request = json.dumps({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0", 
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            })
            
            # Start process
            process = await asyncio.create_subprocess_exec(
                path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send init then tool request
            full_input = init_request + '\n' + request + '\n'
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=full_input.encode()),
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            # Parse tool response
            if stdout:
                lines = stdout.decode().split('\n')
                for line in reversed(lines):  # Check from end
                    if line.strip() and '"result"' in line:
                        try:
                            response = json.loads(line.strip())
                            if 'result' in response:
                                # Extract actual content
                                content = response['result'].get('content', [])
                                if content and isinstance(content, list):
                                    text_content = content[0].get('text', '')
                                    try:
                                        data = json.loads(text_content)
                                        return {
                                            'status': 'success',
                                            'response_time': response_time,
                                            'data': data,
                                            'has_error': 'error' in data
                                        }
                                    except:
                                        return {
                                            'status': 'success',
                                            'response_time': response_time,
                                            'raw_response': text_content[:200]
                                        }
                        except json.JSONDecodeError:
                            continue
            
            return {
                'status': 'no_valid_response',
                'stderr': stderr.decode()[:200] if stderr else None
            }
            
        except asyncio.TimeoutError:
            return {'status': 'timeout'}
        except Exception as e:
            return {'status': 'exception', 'error': str(e)}
    
    def validate_response_data(self, mcp_name: str, tool: str, 
                              data: Any) -> Dict[str, Any]:
        """Validate the quality of response data"""
        validation = {
            'is_valid': True,
            'issues': [],
            'data_quality': 100
        }
        
        # MCP-specific validation
        if mcp_name == 'SEC':
            if tool == 'scrape_10k_financials':
                if isinstance(data, dict):
                    if 'error' in data:
                        validation['is_valid'] = False
                        validation['issues'].append('Error in response')
                        validation['data_quality'] = 0
                    else:
                        # Check for expected fields
                        expected = ['ticker', 'filing_date']
                        for field in expected:
                            if field not in data:
                                validation['issues'].append(f'Missing {field}')
                                validation['data_quality'] -= 20
            
            elif tool == 'get_current_price':
                if isinstance(data, dict) and 'price' in data:
                    price = data.get('price')
                    if isinstance(price, (int, float)) and price > 0:
                        validation['is_valid'] = True
                    else:
                        validation['issues'].append('Invalid price value')
                        validation['data_quality'] = 50
        
        elif mcp_name == 'X-SENTIMENT':
            if tool == 'analyze_ticker_sentiment':
                if isinstance(data, dict):
                    required = ['sentiment_score', 'sentiment_label']
                    for field in required:
                        if field not in data:
                            validation['issues'].append(f'Missing {field}')
                            validation['data_quality'] -= 30
        
        # Add more validations for other MCPs...
        
        return validation
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests on all MCPs"""
        print("🧪 Starting Comprehensive MCP Testing")
        print("=" * 60)
        
        overall_results = {
            'test_date': datetime.now().isoformat(),
            'summary': {
                'total_mcps': len(self.mcps),
                'connected': 0,
                'failed': 0,
                'total_tools_tested': 0,
                'successful_tools': 0
            },
            'mcp_results': {}
        }
        
        # Test each MCP
        for mcp_name, config in self.mcps.items():
            mcp_result = {
                'connection': {},
                'tools': {},
                'overall_status': 'unknown'
            }
            
            # Test connection
            connection_result = await self.test_mcp_connection(
                mcp_name, config['path']
            )
            mcp_result['connection'] = connection_result
            
            if connection_result['status'] == 'connected':
                overall_results['summary']['connected'] += 1
                print(f"  ✅ Connected in {connection_result['response_time']:.2f}s")
                
                # Test each tool
                for tool_name, params in config['tests']:
                    tool_result = await self.test_mcp_tool(
                        mcp_name, config['path'], tool_name, params
                    )
                    
                    overall_results['summary']['total_tools_tested'] += 1
                    
                    # Validate response
                    if tool_result['status'] == 'success':
                        if 'data' in tool_result:
                            validation = self.validate_response_data(
                                mcp_name, tool_name, tool_result['data']
                            )
                            tool_result['validation'] = validation
                            
                            if validation['is_valid']:
                                overall_results['summary']['successful_tools'] += 1
                                print(f"    ✅ {tool_name}: Success ({tool_result['response_time']:.2f}s)")
                            else:
                                print(f"    ⚠️  {tool_name}: Data issues - {validation['issues']}")
                        else:
                            overall_results['summary']['successful_tools'] += 1
                            print(f"    ✅ {tool_name}: Success")
                    else:
                        print(f"    ❌ {tool_name}: {tool_result['status']}")
                    
                    mcp_result['tools'][tool_name] = tool_result
                
                # Determine overall status
                successful_tools = sum(
                    1 for t in mcp_result['tools'].values() 
                    if t['status'] == 'success'
                )
                if successful_tools == len(config['tests']):
                    mcp_result['overall_status'] = 'fully_functional'
                elif successful_tools > 0:
                    mcp_result['overall_status'] = 'partially_functional'
                else:
                    mcp_result['overall_status'] = 'non_functional'
            else:
                overall_results['summary']['failed'] += 1
                mcp_result['overall_status'] = 'connection_failed'
                print(f"  ❌ Connection failed: {connection_result['status']}")
            
            overall_results['mcp_results'][mcp_name] = mcp_result
        
        return overall_results
    
    async def run_integration_test(self) -> Dict[str, Any]:
        """Test MCPs working together"""
        print("\n\n🔗 Running Integration Tests")
        print("=" * 60)
        
        integration_tests = [
            {
                'name': 'Full Stock Analysis',
                'ticker': 'AAPL',
                'steps': [
                    ('SEC', 'get_current_price', {'ticker': 'AAPL'}),
                    ('NEWS-SENTIMENT', 'analyze_news_sentiment', {'ticker': 'AAPL'}),
                    ('X-SENTIMENT', 'analyze_ticker_sentiment', {'ticker': 'AAPL'}),
                    ('ANALYST-RATINGS', 'get_consensus_rating', {'ticker': 'AAPL'})
                ]
            },
            {
                'name': 'Sentiment Triangulation',
                'ticker': 'TSLA',
                'steps': [
                    ('NEWS-SENTIMENT', 'get_aggregate_sentiment', {'ticker': 'TSLA'}),
                    ('X-SENTIMENT', 'analyze_ticker_sentiment', {'ticker': 'TSLA'}),
                    ('ALTERNATIVE-DATA', 'get_reddit_sentiment', {'query': 'TSLA stock'})
                ]
            }
        ]
        
        results = []
        
        for test in integration_tests:
            print(f"\n📋 {test['name']} for {test['ticker']}")
            test_result = {
                'name': test['name'],
                'ticker': test['ticker'],
                'steps': [],
                'success': True
            }
            
            for mcp, tool, params in test['steps']:
                if mcp in self.mcps:
                    result = await self.test_mcp_tool(
                        mcp, self.mcps[mcp]['path'], tool, params
                    )
                    
                    step_result = {
                        'mcp': mcp,
                        'tool': tool,
                        'status': result['status'],
                        'response_time': result.get('response_time', 0)
                    }
                    
                    if result['status'] == 'success':
                        print(f"  ✅ {mcp}.{tool} - {result['response_time']:.2f}s")
                        if 'data' in result:
                            # Extract key metrics
                            data = result['data']
                            if isinstance(data, dict):
                                if 'sentiment_score' in data:
                                    step_result['sentiment'] = data['sentiment_score']
                                elif 'price' in data:
                                    step_result['price'] = data['price']
                                elif 'consensus' in data:
                                    step_result['rating'] = data['consensus']
                    else:
                        print(f"  ❌ {mcp}.{tool} - {result['status']}")
                        test_result['success'] = False
                    
                    test_result['steps'].append(step_result)
            
            results.append(test_result)
        
        return {
            'integration_tests': results,
            'all_passed': all(t['success'] for t in results)
        }
    
    def generate_report(self, test_results: Dict[str, Any], 
                       integration_results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("# 📊 Financial MCP Test Report")
        report.append(f"**Date**: {test_results['test_date']}")
        report.append("")
        
        # Summary
        summary = test_results['summary']
        report.append("## Summary")
        report.append(f"- **MCPs Tested**: {summary['total_mcps']}")
        report.append(f"- **Connected**: {summary['connected']} ✅")
        report.append(f"- **Failed**: {summary['failed']} ❌")
        report.append(f"- **Tools Tested**: {summary['total_tools_tested']}")
        report.append(f"- **Successful**: {summary['successful_tools']}")
        success_rate = (summary['successful_tools'] / summary['total_tools_tested'] * 100 
                       if summary['total_tools_tested'] > 0 else 0)
        report.append(f"- **Success Rate**: {success_rate:.1f}%")
        report.append("")
        
        # Individual MCP Results
        report.append("## MCP Status")
        report.append("")
        
        for mcp_name, result in test_results['mcp_results'].items():
            status_emoji = {
                'fully_functional': '✅',
                'partially_functional': '⚠️',
                'non_functional': '❌',
                'connection_failed': '🔌❌'
            }.get(result['overall_status'], '❓')
            
            report.append(f"### {mcp_name} {status_emoji}")
            
            if result['connection']['status'] == 'connected':
                report.append(f"- Connection: ✅ ({result['connection']['response_time']:.2f}s)")
                
                # Tool results
                if result['tools']:
                    report.append("- Tools:")
                    for tool_name, tool_result in result['tools'].items():
                        if tool_result['status'] == 'success':
                            report.append(f"  - {tool_name}: ✅")
                            if 'validation' in tool_result:
                                val = tool_result['validation']
                                if val['issues']:
                                    report.append(f"    - Issues: {', '.join(val['issues'])}")
                        else:
                            report.append(f"  - {tool_name}: ❌ ({tool_result['status']})")
            else:
                report.append(f"- Connection: ❌ ({result['connection']['status']})")
            
            report.append("")
        
        # Integration Test Results
        if integration_results:
            report.append("## Integration Tests")
            report.append("")
            
            for test in integration_results['integration_tests']:
                status = "✅" if test['success'] else "❌"
                report.append(f"### {test['name']} {status}")
                report.append(f"**Ticker**: {test['ticker']}")
                
                for step in test['steps']:
                    step_status = "✅" if step['status'] == 'success' else "❌"
                    report.append(f"- {step['mcp']}.{step['tool']}: {step_status}")
                    
                    # Show extracted data
                    if 'sentiment' in step:
                        report.append(f"  - Sentiment: {step['sentiment']:.3f}")
                    elif 'price' in step:
                        report.append(f"  - Price: ${step['price']}")
                    elif 'rating' in step:
                        report.append(f"  - Rating: {step['rating']}")
                
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        
        failed_mcps = [
            name for name, result in test_results['mcp_results'].items()
            if result['overall_status'] in ['non_functional', 'connection_failed']
        ]
        
        if failed_mcps:
            report.append("### Failed MCPs requiring attention:")
            for mcp in failed_mcps:
                report.append(f"- {mcp}")
                result = test_results['mcp_results'][mcp]
                if result['connection']['status'] == 'timeout':
                    report.append("  - Issue: Connection timeout")
                    report.append("  - Fix: Check if virtual environment is activated")
                elif 'error' in result['connection']:
                    report.append(f"  - Error: {result['connection']['error'][:100]}")
        else:
            report.append("✅ All MCPs are functional!")
        
        return "\n".join(report)


async def main():
    """Run comprehensive MCP tests"""
    tester = MCPTester()
    
    # Run tests
    print("🚀 Starting Financial MCP Testing Suite\n")
    
    # Comprehensive functionality test
    test_results = await tester.run_comprehensive_test()
    
    # Integration tests
    integration_results = await tester.run_integration_test()
    
    # Generate report
    report = tester.generate_report(test_results, integration_results)
    
    # Save report
    report_path = Path("/Users/LuisRincon/SEC-MCP/FinancialMCPs/test_report.md")
    report_path.write_text(report)
    
    # Save detailed results
    results_path = Path("/Users/LuisRincon/SEC-MCP/FinancialMCPs/test_results.json")
    with open(results_path, 'w') as f:
        json.dump({
            'functionality_tests': test_results,
            'integration_tests': integration_results
        }, f, indent=2)
    
    print(f"\n\n✅ Testing complete!")
    print(f"📄 Report saved to: {report_path}")
    print(f"📊 Detailed results: {results_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = test_results['summary']
    print(f"MCPs Connected: {summary['connected']}/{summary['total_mcps']}")
    print(f"Tools Working: {summary['successful_tools']}/{summary['total_tools_tested']}")
    print(f"Integration Tests: {'✅ PASSED' if integration_results['all_passed'] else '❌ FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())