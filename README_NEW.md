# Currency Risk Management System

A comprehensive web application for managing currency risk in international trade transactions with Letter of Credit (LC) management, real-time forex data integration, and forward rates analysis.

## 🚀 Live Demo

**Access the application**: Will be deployed to Heroku soon!

## 🎯 Features

### Core Features
- ✅ **Letter of Credit Management** - Create and track international trade LCs
- ✅ **Real-time Forex Data** - Live USD/INR exchange rates with multiple fallback sources
- ✅ **P&L Calculations** - Spot and forward rate-based profit/loss analysis
- ✅ **Forward Rates Analysis** - Daily forward rates tracking and P&L projections
- ✅ **Risk Analytics** - Value at Risk (VaR), volatility, and risk metrics
- ✅ **Scenario Analysis** - Multiple exit scenarios and hold-to-maturity comparisons
- ✅ **Professional Reporting** - Excel and JSON reports with visualizations
- ✅ **Interactive Dashboard** - Web-based interface for monitoring and analysis
- ✅ **Alert System** - Automated notifications for significant P&L changes

### Advanced Features
- 📊 **Forward Rates P&L** - Daily tracking of market expectations for LC maturity dates
- 🎯 **Exit Strategy Analysis** - Compare early exit vs hold-to-maturity scenarios  
- 📈 **Trend Analysis** - Forward rate trends and volatility calculations
- 🔔 **Smart Alerts** - Configurable thresholds for P&L and rate changes
- 📑 **Executive Reports** - Management-ready summaries and recommendations

## 🏗️ System Architecture

```
├── Web Interface (Flask)
├── LC Management System
├── Forex Data Providers (Multiple Sources)
├── Forward Rates Engine
├── P&L Calculators (Spot + Forward)
├── Risk Analytics Engine
├── Report Generators
├── Alert System
└── Database (SQLite/PostgreSQL)
```

## 🔧 Technology Stack

- **Backend**: Python 3.9+, Flask
- **Database**: SQLite (development), PostgreSQL (production)
- **Data Sources**: Yahoo Finance, ExchangeRate-API, FreeCurrencyAPI
- **Visualization**: Plotly, Matplotlib
- **Reports**: openpyxl, pandas
- **Deployment**: Heroku
- **Frontend**: HTML5, Bootstrap, JavaScript

## 📦 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/RudraS025/currency_risk_management.git
   cd currency_risk_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   ```
   http://localhost:5000
   ```

## 📊 Sample Data & Results

### Example LC - Paddy Export to Iran
- **Amount**: $400,000 USD (1000 tons @ $400/ton)
- **Signed**: June 16, 2025
- **Maturity**: September 14, 2025 (90 days)

### Live Analysis Results
- **Current P&L**: ₹-212,878.42 (-0.62%)
- **Forward P&L**: ₹-243,381.31 (-0.71%)
- **Risk Level**: 🟢 LOW RISK
- **Best Exit Strategy**: August 29, 2025 (-0.66% P&L)

## 🎯 Quick Start Examples

### 1. Create a Letter of Credit
```python
from src.currency_risk_mgmt.models.letter_of_credit import LetterOfCredit

lc = LetterOfCredit(
    lc_id="EXPORT-001",
    commodity="Basmati Rice",
    quantity=1000,
    unit="tons",
    rate_per_unit=400,
    currency="USD",
    signing_date="2025-06-16",
    maturity_days=90,
    customer_country="Iran"
)
```

### 2. Calculate Current P&L
```python
from src.currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator

pl_calculator = ProfitLossCalculator()
result = pl_calculator.calculate_current_pl(lc, "INR")
print(f"Current P&L: ₹{result['unrealized_pl']:,.2f}")
```

### 3. Analyze Forward Rates
```python
from src.currency_risk_mgmt.calculators.forward_pl_calculator import ForwardPLCalculator

forward_calculator = ForwardPLCalculator()
forward_report = forward_calculator.generate_forward_pl_report(lc, "INR")
```

## 🔌 Data Sources & Integration

### Current Open Source APIs
- **Yahoo Finance** - Primary forex data source
- **ExchangeRate-API** - Historical rates and backup
- **FreeCurrencyAPI** - Additional rate verification

### Production Ready Integrations
- Bank FX Desks (HDFC, ICICI, SBI, Axis)
- Bloomberg Terminal API
- Reuters Eikon
- RBI (Reserve Bank of India)

## 📈 Web Dashboard Features

### Main Dashboard
- Portfolio overview with total exposure
- Real-time P&L tracking
- Forward rates analysis
- Risk alerts and notifications

### Reports & Analytics
- Executive summary reports
- Daily P&L trends
- Forward rates projections
- Exit scenario analysis
- Professional Excel/JSON exports

## 🚀 Deployment

### Heroku Deployment
The application is configured for Heroku with:
- `Procfile` for web dyno configuration
- `requirements.txt` for dependencies
- Environment variable configuration
- PostgreSQL database integration

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_URL=postgres://...
export SECRET_KEY=your_secret_key
```

## 📞 Support

For support and questions:
- **GitHub Issues**: [Create an issue](https://github.com/RudraS025/currency_risk_management/issues)
- **Email**: rudra.s.25@gmail.com
- **Documentation**: Available in the `/docs` folder

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built for international trade professionals** 🌍💱📊
