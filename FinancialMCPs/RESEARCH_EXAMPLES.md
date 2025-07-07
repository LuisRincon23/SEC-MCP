# Research Administrator Examples

## 🚀 Quick Start Examples

### 1. Basic Research Request
```
"Use RESEARCH-ADMIN's create_research_plan tool to analyze AAPL"
```

### 2. Quick Investment Check (5 min)
```
"Use RESEARCH-ADMIN's create_research_plan tool with ticker TSLA and depth quick"
```

### 3. Standard Analysis (15 min)
```
"Use RESEARCH-ADMIN's create_research_plan tool with ticker MSFT, depth standard, and sector technology"
```

### 4. Deep Dive Research (45 min)
```
"Use RESEARCH-ADMIN's create_research_plan tool with ticker AMZN, depth deep, sector technology, and focus_areas ['cloud growth', 'AI investments', 'retail margins']"
```

### 5. Natural Language Processing
```
"Use RESEARCH-ADMIN's parse_research_request tool with request 'Is Netflix a good buy after earnings?'"
```

## 📊 Complete Workflow Example

### Step 1: Create Research Plan
```
Use RESEARCH-ADMIN's create_research_plan tool with:
- ticker: "NVDA"
- depth: "standard"
- sector: "technology"
- focus_areas: ["AI chip demand", "data center growth"]
```

### Step 2: Execute the Plan
The Research Administrator will return a plan with specific MCP calls like:
1. Use SEC-SCRAPER's scrape_10k_financials with ticker "NVDA"
2. Use SEC-SCRAPER's get_current_price with ticker "NVDA"
3. Use INDUSTRY-ASSUMPTIONS's generate_full_dcf_assumptions with ticker "NVDA" and industry "technology"
4. Use NEWS-SENTIMENT's get_aggregate_sentiment with ticker "NVDA"
5. Use ANALYST-RATINGS's get_consensus_rating with ticker "NVDA"
6. Use INSTITUTIONAL's track_institutional_changes with ticker "NVDA"

### Step 3: Generate Report Outline
After collecting data:
```
Use RESEARCH-ADMIN's generate_report_outline with:
- ticker: "NVDA"
- collected_data: {
    "sec_data": true,
    "sentiment_data": true,
    "analyst_data": true,
    "institutional_data": true,
    "dcf_data": true
  }
```

### Step 4: Create Executive Summary
```
Use RESEARCH-ADMIN's generate_executive_summary with:
- ticker: "NVDA"
- key_findings: {
    "recommendation": "BUY",
    "price_target": 850,
    "upside": 25,
    "conviction": "High",
    "valuation_thesis": "Trading below DCF fair value despite AI leadership",
    "momentum_thesis": "Strong institutional buying and positive sentiment",
    "growth_thesis": "Data center revenue accelerating, confirmed by hiring data",
    "main_risk": "Valuation multiple compression if growth slows",
    "catalyst": "Next-gen chip announcement"
  }
```

## 🎯 Sector-Specific Examples

### Technology Sector
```
{
  "ticker": "META",
  "depth": "standard",
  "sector": "technology",
  "focus_areas": ["metaverse ROI", "ad revenue recovery", "AI infrastructure"]
}
```

### Financial Sector
```
{
  "ticker": "BAC",
  "depth": "standard",
  "sector": "finance",
  "focus_areas": ["net interest margin", "loan loss provisions", "trading revenue"]
}
```

### Healthcare/Biotech
```
{
  "ticker": "PFE",
  "depth": "deep",
  "sector": "healthcare",
  "focus_areas": ["pipeline value", "patent cliffs", "M&A strategy"]
}
```

### Energy Sector
```
{
  "ticker": "CVX",
  "depth": "standard",
  "sector": "energy",
  "focus_areas": ["production growth", "capex discipline", "dividend sustainability"]
}
```

### Retail Sector
```
{
  "ticker": "TGT",
  "depth": "standard",
  "sector": "retail",
  "focus_areas": ["inventory management", "e-commerce growth", "margin pressure"]
}
```

## 📈 Advanced Research Scenarios

### Earnings Analysis
```
"Parse this request: Analyze GOOGL after earnings miss, focus on cloud and AI"
```

### M&A Target Analysis
```
{
  "ticker": "ATVI",
  "depth": "deep",
  "focus_areas": ["acquisition premium", "regulatory risks", "synergies"]
}
```

### Turnaround Situation
```
{
  "ticker": "DIS",
  "depth": "deep",
  "focus_areas": ["streaming profitability", "parks recovery", "content strategy"]
}
```

### High Growth Tech
```
{
  "ticker": "SNOW",
  "depth": "standard",
  "focus_areas": ["revenue growth sustainability", "path to profitability", "competitive moat"]
}
```

## 🔄 Multi-Stock Comparison

### Compare Tech Giants
```
First: Create research plan for AAPL with depth "quick"
Then: Create research plan for MSFT with depth "quick"
Then: Create research plan for GOOGL with depth "quick"
Finally: Compare the executive summaries
```

### Sector Screening
```
"Parse request: Quick check on top 5 semiconductor stocks for AI exposure"
```

## 💡 Tips for Best Results

1. **Always specify sector** for accurate DCF assumptions
2. **Use focus_areas** to target specific concerns
3. **Start with "standard" depth** unless you need quick/deep
4. **Chain multiple requests** for comparative analysis
5. **Use natural language** for complex requests

## 🎪 Complete Example Conversation

```
User: "I'm interested in investing in AI stocks. Can you analyze Nvidia?"