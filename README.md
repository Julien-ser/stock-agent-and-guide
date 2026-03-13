# Stock Agent and Guide

**Mission:** Create a stock agent that pulls the best stocks in 5 key financial categories and provides a guide for users to find these metrics themselves.

---

## Overview

This project consists of two main components:

1. **Stock Agent** - Automatically analyzes stocks and ranks them by:
   - Profit Margin
   - Operating Margin
   - Free Cash Flow
   - Return on Invested Capital (ROIC)
   - Interest Coverage Ratio

2. **User Guide** - Educational documentation showing how to find these metrics manually

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the stock analysis agent
python -m src.cli --help
```

---

## Project Structure

```
stock-agent-and-guide/
├── src/
│   ├── stock_agent.py      # Main agent logic
│   ├── data_fetcher.py     # Fetch financial data from Yahoo Finance
│   ├── analyzer.py         # Calculate and rank metrics
│   ├── guide_generator.py  # Generate user guide
│   └── cli.py              # Command-line interface
├── tests/
│   ├── test_data_fetcher.py
│   └── test_analyzer.py
├── output/                 # Analysis results and guides
├── data/                   # Data caching
├── requirements.txt
└── README.md
```

---

## Usage

```bash
# Analyze top stocks in all categories
python -m src.cli analyze --universe sp500

# Generate user guide
python -m src.cli generate-guide

# Both operations
python -m src.cli full-run
```

---

## Current Progress

- [x] Architecture design complete
- [x] Dependencies installation
- [ ] Core implementation
- [ ] Testing
- [ ] Documentation
- [ ] Deployment

---

## License

MIT
