# 📊 Financial MCP Test Report
**Date**: 2025-07-07T17:54:22.349863

## Summary
- **MCPs Tested**: 9
- **Connected**: 9 ✅
- **Failed**: 0 ❌
- **Tools Tested**: 27
- **Successful**: 0
- **Success Rate**: 0.0%

## MCP Status

### SEC ❌
- Connection: ✅ (0.95s)
- Tools:
  - scrape_10k_financials: ❌ (no_valid_response)
  - parse_xbrl_data: ❌ (no_valid_response)
  - get_current_price: ❌ (no_valid_response)

### NEWS-SENTIMENT ❌
- Connection: ✅ (0.39s)
- Tools:
  - analyze_news_sentiment: ❌ (no_valid_response)
  - get_aggregate_sentiment: ❌ (no_valid_response)
  - analyze_earnings_sentiment: ❌ (no_valid_response)

### X-SENTIMENT ❌
- Connection: ✅ (0.39s)
- Tools:
  - analyze_ticker_sentiment: ❌ (no_valid_response)
  - compare_tickers_sentiment: ❌ (no_valid_response)
  - sentiment_alerts: ❌ (no_valid_response)

### ANALYST-RATINGS ❌
- Connection: ✅ (0.56s)
- Tools:
  - get_consensus_rating: ❌ (no_valid_response)
  - get_price_targets: ❌ (no_valid_response)
  - track_rating_changes: ❌ (no_valid_response)

### INSTITUTIONAL ❌
- Connection: ✅ (0.34s)
- Tools:
  - get_institutional_holdings: ❌ (no_valid_response)
  - track_ownership_changes: ❌ (no_valid_response)
  - get_top_holders: ❌ (no_valid_response)

### ALTERNATIVE-DATA ❌
- Connection: ✅ (0.35s)
- Tools:
  - analyze_hiring_trends: ❌ (no_valid_response)
  - get_reddit_sentiment: ❌ (no_valid_response)
  - track_web_traffic: ❌ (no_valid_response)

### INDUSTRY-ASSUMPTIONS ❌
- Connection: ✅ (0.40s)
- Tools:
  - calculate_industry_wacc: ❌ (no_valid_response)
  - get_sector_assumptions: ❌ (no_valid_response)
  - benchmark_metrics: ❌ (no_valid_response)

### ECONOMIC-DATA ❌
- Connection: ✅ (0.54s)
- Tools:
  - get_economic_indicators: ❌ (no_valid_response)
  - analyze_market_regime: ❌ (no_valid_response)
  - get_fed_data: ❌ (no_valid_response)

### RESEARCH-ADMIN ❌
- Connection: ✅ (0.26s)
- Tools:
  - create_research_summary: ❌ (no_valid_response)
  - generate_investment_thesis: ❌ (no_valid_response)
  - compile_comprehensive_report: ❌ (no_valid_response)

## Integration Tests

### Full Stock Analysis ❌
**Ticker**: AAPL
- SEC.get_current_price: ❌
- NEWS-SENTIMENT.analyze_news_sentiment: ❌
- X-SENTIMENT.analyze_ticker_sentiment: ❌
- ANALYST-RATINGS.get_consensus_rating: ❌

### Sentiment Triangulation ❌
**Ticker**: TSLA
- NEWS-SENTIMENT.get_aggregate_sentiment: ❌
- X-SENTIMENT.analyze_ticker_sentiment: ❌
- ALTERNATIVE-DATA.get_reddit_sentiment: ❌

## Recommendations
### Failed MCPs requiring attention:
- SEC
- NEWS-SENTIMENT
- X-SENTIMENT
- ANALYST-RATINGS
- INSTITUTIONAL
- ALTERNATIVE-DATA
- INDUSTRY-ASSUMPTIONS
- ECONOMIC-DATA
- RESEARCH-ADMIN