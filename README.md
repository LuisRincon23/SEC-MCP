# Financial MCPs - PhD-Level Research Tools for Claude Code CLI

A comprehensive collection of advanced Model Context Protocol (MCP) servers that transform Claude Code CLI into an institutional-grade financial research platform.

<div align="center">

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-blue)](https://modelcontextprotocol.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-CLI-purple)](https://github.com/anthropics/claude-cli)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**8 Specialized MCPs** • **PhD-Level Analysis** • **Institutional Quality**

</div>

## 🎓 Overview

This repository contains 8 specialized MCP servers that provide Claude Code CLI with capabilities rivaling professional financial platforms used by hedge funds and investment banks:

| MCP | Description | Key Features |
|-----|-------------|--------------|
| **SEC Scraper** | XBRL parsing & comprehensive analysis | DCF modeling, Monte Carlo simulations |
| **News Sentiment** | Advanced NLP for financial text | Context-aware sentiment, earnings call analysis |
| **Analyst Ratings** | Consensus tracking & peer comparison | Rating aggregation, price target analysis |
| **Institutional** | Ownership & fund flow analysis | 13F tracking, insider transactions |
| **Alternative Data** | Web scraping for unique insights | Hiring trends, social sentiment, reviews |
| **Industry Assumptions** | Sector analysis & modeling | WACC calculations, peer metrics |
| **Economic Data** | Macro indicators & regime detection | Fed data, employment, inflation |
| **Research Admin** | Report generation & orchestration | 25+ page institutional reports |

## 🚀 Features

### Advanced Financial Analysis
- **XBRL Parsing**: Extract 50+ structured metrics from SEC filings
- **DCF Valuation**: Monte Carlo simulations with 10,000 iterations
- **Financial Metrics**: ROE, ROIC, Altman Z-Score, Piotroski F-Score
- **Peer Comparison**: Automatic competitor identification and analysis

### Market Intelligence
- **PhD-Level NLP**: Context-aware sentiment analysis for earnings calls
- **Technical Analysis**: RSI, MACD, Bollinger Bands, support/resistance
- **Market Regime Detection**: Bull/bear market identification
- **Sector Rotation**: Industry trend and momentum analysis

### Research Output
- **Institutional Reports**: Professional 25+ page equity research documents
- **Investment Thesis**: Comprehensive bull/bear cases with catalysts
- **Risk Assessment**: Multi-factor risk scoring and analysis
- **Quality Metrics**: Data completeness and confidence scoring

## 📦 Installation

### Prerequisites
- Python 3.10+
- Claude Code CLI (`npm install -g @anthropic-ai/claude-cli`)
- uv package manager (`pip install uv`)

### Quick Setup

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/financial-mcps.git
cd financial-mcps
```

2. **Create and activate virtual environment**:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
uv sync
```

4. **Add all MCPs to Claude Code CLI**:
```bash
# Run the setup script
./setup_all_mcps.sh

# Or manually add each MCP:
claude mcp add SEC "./FinancialMCPs/SEC_SCRAPER_MCP/start-mcp.sh" --transport stdio
claude mcp add NEWS-SENTIMENT "./FinancialMCPs/NEWS_SENTIMENT_SCRAPER/start-mcp.sh" --transport stdio
claude mcp add ANALYST-RATINGS "./FinancialMCPs/ANALYST_RATINGS_SCRAPER/start-mcp.sh" --transport stdio
claude mcp add INSTITUTIONAL "./FinancialMCPs/INSTITUTIONAL_SCRAPER/start-mcp.sh" --transport stdio
claude mcp add ALTERNATIVE-DATA "./FinancialMCPs/ALTERNATIVE_DATA_SCRAPER/start-mcp.sh" --transport stdio
claude mcp add INDUSTRY-ASSUMPTIONS "./FinancialMCPs/INDUSTRY_ASSUMPTIONS_ENGINE/start-mcp.sh" --transport stdio
claude mcp add ECONOMIC-DATA "./FinancialMCPs/ECONOMIC_DATA_COLLECTOR/start-mcp.sh" --transport stdio
claude mcp add RESEARCH-ADMIN "./FinancialMCPs/RESEARCH_ADMINISTRATOR/start-mcp.sh" --transport stdio
```

5. **Verify installation**:
```bash
claude mcp list
# Should show all 8 Financial MCPs
```

## 💡 Usage Examples

### Basic Commands

```bash
# Get current stock price
Use SEC to get current price for ticker "AAPL"

# Analyze sentiment
Use NEWS-SENTIMENT to analyze sentiment for ticker "MSFT"

# Get analyst consensus
Use ANALYST-RATINGS to get consensus rating for ticker "GOOGL"
```

### Advanced Analysis

```bash
# Comprehensive stock analysis (PhD-level)
Use SEC to perform comprehensive analysis for ticker "NVDA"

# Generate institutional research report
Use RESEARCH-ADMIN to generate research report for ticker "TSLA"

# Sector analysis
Use INDUSTRY-ASSUMPTIONS to analyze sector "Technology"
```

### Professional Workflows

#### Investment Research Workflow
```bash
1. Use SEC to perform comprehensive analysis for ticker "META"
2. Use NEWS-SENTIMENT to analyze earnings call sentiment for ticker "META"  
3. Use ANALYST-RATINGS to compare with peer ratings
4. Use RESEARCH-ADMIN to generate investment thesis
```

#### Risk Assessment Workflow
```bash
1. Use SEC to calculate Altman Z-Score for ticker "GME"
2. Use INSTITUTIONAL to track ownership changes
3. Use ECONOMIC-DATA to assess macro risks
4. Use ALTERNATIVE-DATA to gauge social sentiment
```

## 🏗️ Architecture

```
financial-mcps/
├── FinancialMCPs/
│   ├── SEC_SCRAPER_MCP/           # XBRL parsing, DCF modeling
│   ├── NEWS_SENTIMENT_SCRAPER/    # Advanced NLP sentiment
│   ├── ANALYST_RATINGS_SCRAPER/   # Consensus tracking
│   ├── INSTITUTIONAL_SCRAPER/     # Ownership analysis
│   ├── ALTERNATIVE_DATA_SCRAPER/  # Web scraping
│   ├── INDUSTRY_ASSUMPTIONS/      # Sector analysis
│   ├── ECONOMIC_DATA_COLLECTOR/   # Macro indicators
│   ├── RESEARCH_ADMINISTRATOR/    # Report generation
│   └── shared/                    # Shared advanced modules
│       ├── financial_analysis.py  # DCF, metrics calculations
│       ├── xbrl_parser.py        # XBRL data extraction
│       ├── advanced_nlp.py       # PhD-level NLP
│       ├── research_report_generator.py
│       └── data_cache.py         # Intelligent caching
├── setup_all_mcps.sh             # Quick setup script
├── test_phd_features.py          # Integration tests
├── requirements.txt
├── README.md
└── LICENSE
```

## 🔧 Configuration

### MCP-Specific Settings

Each MCP can be configured through environment variables:
```bash
export CACHE_DIR="/tmp/financial_mcp_cache"
export LOG_LEVEL="INFO"
export RATE_LIMIT_DELAY="1.0"  # SEC compliance
```

### Analysis Parameters

Edit `analysis_config` in each MCP's main.py:
```python
self.analysis_config = {
    'dcf_years': 5,              # DCF projection years
    'peer_count': 10,            # Number of peers to analyze
    'monte_carlo_simulations': 10000,  # Simulation count
    'confidence_threshold': 0.8   # Minimum confidence score
}
```

### Cache Settings

Configure cache TTL in `shared/data_cache.py`:
```python
self.ttl_config = {
    'price_data': timedelta(minutes=5),
    'financial_statements': timedelta(days=90),
    'news': timedelta(hours=1),
    'research_reports': timedelta(days=30)
}
```

## 🧪 Testing

### Run All Tests
```bash
python test_phd_features.py
```

### Test Individual MCPs
```bash
./test_single_mcp.sh SEC_SCRAPER_MCP
```

### Debug Mode
```bash
claude --debug
# Then use any MCP command to see detailed logs
```

## 📊 Data Sources

- **SEC EDGAR**: Official filings, XBRL data
- **Yahoo Finance**: Real-time prices, basic metrics
- **Finviz**: News aggregation, analyst ratings
- **MarketWatch**: Additional market data
- **Federal Reserve**: Economic indicators
- **Alternative Sources**: Indeed, Glassdoor, Reddit, Google Trends

## 🔒 Security & Compliance

- **Rate Limiting**: Built-in delays to respect data source limits
- **User Agent**: Proper identification for web scraping
- **Caching**: Reduces redundant requests
- **Data Validation**: Ensures data quality and accuracy

## ⚠️ Disclaimer

These tools are for **educational and research purposes only**. Not intended for:
- Production trading systems
- Real money investment decisions
- High-frequency trading
- Regulatory compliance

Always verify data independently and conduct your own due diligence.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Feature request procedure

## 📈 Roadmap

- [ ] Bloomberg/Refinitiv data integration
- [ ] Real-time streaming capabilities
- [ ] Machine learning predictions
- [ ] Options analytics
- [ ] Portfolio optimization
- [ ] Backtesting framework

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for [Claude Code CLI](https://github.com/anthropics/claude-cli) by Anthropic
- Inspired by institutional research platforms
- Uses publicly available financial data sources
- Special thanks to the MCP community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/financial-mcps/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/financial-mcps/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/financial-mcps/wiki)

---

**Note**: This is an advanced financial research toolkit. Users should have a solid understanding of financial analysis and Python programming. These MCPs provide PhD-level analysis capabilities previously only available to institutional investors.