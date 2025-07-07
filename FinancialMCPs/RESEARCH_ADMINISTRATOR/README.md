# Research Administrator MCP

## Overview

The Research Administrator is a master orchestrator MCP that coordinates all 7 financial data MCPs to generate comprehensive investment research reports. It can produce professional-grade analysis in 15 minutes that would normally take 5+ hours of manual research.

## Features

- **Intelligent Orchestration**: Coordinates multiple MCPs in parallel for efficient data collection
- **Multiple Research Depths**: From 5-minute quick checks to 2-hour deep dives
- **Natural Language Processing**: Understands research requests in plain English
- **Professional Templates**: Generates reports formatted like top-tier Wall Street research
- **Comprehensive Coverage**: Combines SEC filings, sentiment, analyst ratings, alternative data, and more

## Research Depth Levels

### 1. Quick Check (5 minutes)
- Current valuation vs peers
- Basic DCF analysis
- Analyst consensus
- Simple Buy/Hold/Sell recommendation

### 2. Standard Analysis (15 minutes) - DEFAULT
- Executive summary with key findings
- DCF model with sensitivity analysis
- Multi-source sentiment analysis
- Institutional flow assessment
- Alternative data signals
- Bull/bear cases with evidence
- Risk factor analysis
- 12-month price target

### 3. Deep Dive (45 minutes)
- Comprehensive 10-15 page research report
- Multiple DCF scenarios
- Historical performance patterns
- Competitive positioning
- Management assessment
- Detailed risk/reward framework

### 4. Sector Analysis (2+ hours)
- Entire sector overview
- Top 10 companies ranked
- Industry-wide DCF comparison
- Relative value analysis
- Thematic opportunities

## Available Tools

### create_research_plan
Creates a comprehensive research plan for a stock.

**Example:**
```json
{
  "ticker": "AAPL",
  "depth": "standard",
  "sector": "technology"
}
```

### parse_research_request
Converts natural language into MCP commands.

**Example:**
```json
{
  "request": "Generate a quick investment check for TSLA"
}
```

### generate_report_outline
Creates a report outline based on collected data.

### list_available_mcps
Shows all available MCPs and their tools.

### generate_executive_summary
Creates an executive summary from research findings.

## How It Works

The Research Administrator coordinates these MCPs:

1. **SEC_SCRAPER**: Financial statements, SEC filings
2. **NEWS_SENTIMENT**: News sentiment from multiple sources
3. **ANALYST_RATINGS**: Wall Street ratings and targets
4. **INSTITUTIONAL**: Smart money flows, insider trading
5. **ALTERNATIVE_DATA**: Job postings, web traffic, patents
6. **INDUSTRY_ASSUMPTIONS**: DCF parameters, sector metrics
7. **ECONOMIC_DATA**: Macro indicators, Fed data

## Example Usage in Claude Desktop

### Quick Investment Check
```
"Use RESEARCH_ADMINISTRATOR to create a quick investment check for NVDA"
```

### Standard Analysis
```
"Use RESEARCH_ADMINISTRATOR to perform comprehensive analysis for MSFT"
```

### Deep Research
```
"Use RESEARCH_ADMINISTRATOR to conduct deep research on AMZN with focus on cloud growth"
```

### Natural Language Request
```
"Use RESEARCH_ADMINISTRATOR to analyze whether Apple is a good buy right now"
```

## Integration with Claude Desktop

1. Add to your `claude_desktop_config.json`:
```json
{
  "RESEARCH-ADMIN": {
    "command": "/Users/LuisRincon/SEC-MCP/FinancialMCPs/RESEARCH_ADMINISTRATOR/start-mcp.sh"
  }
}
```

2. Restart Claude Desktop

3. The Research Administrator will coordinate all other MCPs automatically

## Research Workflow

When you request research, the Administrator:

1. **Parses your request** to understand ticker, depth, and focus areas
2. **Creates a research plan** with specific MCP calls
3. **Orchestrates data collection** in optimal parallel/sequential order
4. **Provides execution instructions** for Claude to follow
5. **Generates report templates** for consistent formatting

## Output Format

Research reports include:

- **Executive Summary**: Key findings and recommendation
- **Financial Overview**: Valuation metrics and comparisons
- **DCF Analysis**: Fair value with sensitivity
- **Sentiment Analysis**: News, social, and analyst sentiment
- **Institutional Activity**: Smart money flows
- **Alternative Signals**: Hiring, web traffic, patents
- **Investment Thesis**: Bull and bear cases
- **Risk Assessment**: Key risks and mitigants
- **Price Target**: 12-month target with rationale

## Best Practices

1. **Start with Standard Analysis** (15 min) for most stocks
2. **Use Quick Check** for rapid screening of multiple stocks
3. **Reserve Deep Dive** for high-conviction ideas
4. **Specify sector** for more accurate DCF assumptions
5. **Add focus areas** for targeted analysis (e.g., "focus on AI revenue")

## Limitations

- Relies on web scraping (respects robots.txt)
- Data freshness depends on source update frequency
- Some alternative data may be estimates
- Not suitable for real-time trading

## Example Research Commands

### Technology Stock Analysis
```
{
  "ticker": "GOOGL",
  "depth": "standard",
  "sector": "technology",
  "focus_areas": ["AI monetization", "cloud growth"]
}
```

### Financial Sector Deep Dive
```
{
  "ticker": "JPM",
  "depth": "deep",
  "sector": "finance",
  "focus_areas": ["interest rate sensitivity", "credit quality"]
}
```

### Quick Biotech Check
```
{
  "ticker": "MRNA",
  "depth": "quick",
  "sector": "healthcare"
}
```

## Troubleshooting

If the Research Administrator has issues:

1. Ensure all 7 financial MCPs are properly connected
2. Check that you have internet connectivity
3. Verify the virtual environment is activated
4. Review logs for specific MCP errors

## Future Enhancements

- Real-time monitoring mode
- Portfolio-level analysis
- Custom report templates
- Excel/PDF export
- Comparative analysis across multiple tickers
- ESG integration