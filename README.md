# Currency Risk Management System

A comprehensive software solution for managing currency risk in international trade transactions, specifically designed for tracking Letter of Credit (LC) operations and calculating profit & loss in real-time.

## Features

- **Letter of Credit Management**: Track LC details, signing dates, maturity dates, and transaction parameters
- **Real-time Forex Data**: Fetch live USD/INR exchange rates from multiple sources
- **P&L Calculations**: Calculate profit and loss at any point from LC signing to maturity
- **Risk Analysis**: Analyze currency exposure and potential risks
- **Financial Reporting**: Generate comprehensive reports and visualizations

## Example Scenario - Live Results

Your client sells 1000 tons of paddy to Iran:
- **Quantity**: 1000 tons
- **Rate**: USD 400/ton
- **Total Value**: USD 400,000
- **LC Signed**: 16.06.2025
- **LC Duration**: 90 days
- **Maturity**: 14.09.2025

### Current Analysis Results (as of June 30, 2025):
- **Current USD/INR Rate**: 85.7170
- **LC Value at Signing**: ₹34,499,679.57
- **Current LC Value**: ₹34,286,801.15
- **Unrealized P&L**: ₹-212,878.42 (-0.62%)
- **Daily P&L**: ₹-15,205.60
- **Days Remaining**: 75 days
- **Risk Level**: 🟢 LOW RISK
- **Value at Risk (95%)**: ₹1,197,953.00 (3.49%)
- **Forward Rate Projection**: 86.0693 (P&L: ₹-71,973.76)

The system successfully fetches real-time USD/INR rates and calculates comprehensive risk metrics.

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Installation**:
   ```bash
   python test_installation.py
   ```

3. **Run Demo Example**:
   ```bash
   python examples/demo_paddy_export.py
   ```

## Key Features Demonstrated

✅ **Real-time Forex Data**: Fetches USD/INR rates from multiple sources  
✅ **Profit & Loss Tracking**: Calculates unrealized P&L from signing to current date  
✅ **Risk Analysis**: Value at Risk (VaR) and Expected Shortfall calculations  
✅ **Forward Rate Projections**: Estimates future exchange rates and P&L  
✅ **Scenario Analysis**: Shows P&L impact of different exchange rate scenarios  
✅ **Comprehensive Reporting**: Generates Excel and JSON reports  
✅ **Data Source Redundancy**: Multiple forex APIs with fallback mechanisms  

## Generated Reports

The system generates:
- **JSON Report**: Complete data structure for programmatic access
- **Excel Report**: Formatted spreadsheets with multiple tabs
- **Interactive Charts**: HTML charts for web viewing
- **Risk Dashboards**: Portfolio-level risk visualization

## Usage

```python
from currency_risk_mgmt import LetterOfCredit, ForexDataProvider, ProfitLossCalculator

# Create LC
lc = LetterOfCredit(
    lc_id="LC001",
    commodity="Paddy",
    quantity=1000,
    unit="tons",
    rate_per_unit=400,
    currency="USD",
    signing_date="2025-06-16",
    maturity_days=90,
    customer_country="Iran"
)

# Calculate current P&L
calculator = ProfitLossCalculator()
current_pl = calculator.calculate_current_pl(lc)
print(f"Current P&L: ₹{current_pl:,.2f}")
```

## Project Structure

```
Currency_Risk_Management/
├── src/
│   ├── currency_risk_mgmt/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── letter_of_credit.py
│   │   │   └── transaction.py
│   │   ├── data_providers/
│   │   │   ├── __init__.py
│   │   │   ├── forex_provider.py
│   │   │   └── rate_sources.py
│   │   ├── calculators/
│   │   │   ├── __init__.py
│   │   │   ├── profit_loss.py
│   │   │   └── risk_metrics.py
│   │   ├── reports/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py
│   │   │   └── visualizations.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── date_utils.py
│   │       └── validators.py
├── tests/
├── examples/
├── docs/
├── requirements.txt
└── README.md
```

## License

MIT License
