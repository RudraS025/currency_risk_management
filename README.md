# Currency Risk Management System

**A comprehensive solution for managing currency risk in international trade transactions using real forward exchange rates.**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 **Key Features**

### **Real Market Data Integration**
- ✅ **78 actual forward rates** from June-September 2025
- ✅ **Time-varying USD/INR rates** (84.25 to 86.56)
- ✅ **Realistic P&L calculations** using real market data
- ✅ **Professional risk analytics** with VaR and volatility metrics

### **Web Dashboard**
- 🎨 **Modern responsive UI** with interactive charts
- 📊 **Real-time P&L visualization** using Chart.js
- 📈 **Scenario analysis** for different market conditions
- 📋 **Comprehensive risk reports** for decision-making

### **API Endpoints**
- 🔍 **Health Check**: System status and data availability
- 💰 **P&L Calculation**: Daily profit/loss analysis
- 📊 **Risk Metrics**: VaR, volatility, confidence intervals
- 🎯 **Scenario Analysis**: Multiple rate scenarios
- 📄 **Report Generation**: Professional risk assessments

## 🚀 **Live Demo**

**Heroku Deployment**: https://rudra-currency-risk-mgmt-ddb4fd04b3f8.herokuapp.com

### **Sample Results**
- **$500,000 USD LC** → **₹12,04,999 profit** (3-month period)
- **78 data points** with realistic forward rate progression
- **8.06% volatility** with ₹1,19,000 Value at Risk (95% confidence)

## 📦 **Installation**

### **Prerequisites**
- Python 3.8+
- pip package manager
- Git

### **Local Setup**
```bash
# Clone the repository
git clone https://github.com/yourusername/currency-risk-management.git
cd currency-risk-management

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 **API Usage**

### **Calculate P&L**
```bash
curl -X POST http://localhost:5000/api/calculate-pl \
  -H "Content-Type: application/json" \
  -d '{
    "lc_number": "LC-2025-001",
    "amount_usd": 500000,
    "issue_date": "2025-06-01",
    "maturity_date": "2025-09-01",
    "beneficiary": "Export Company",
    "commodity": "Technology Equipment"
  }'
```

### **Response Format**
```json
{
  "success": true,
  "data": {
    "total_pl_inr": 1204999.99,
    "spot_rate": 86.56,
    "original_rate": 84.15,
    "pl_percentage": 2.86,
    "days_remaining": 0,
    "daily_pl": [...],
    "data_source": "Real_2025_Market_Data"
  },
  "risk_metrics": {
    "var_95": 119000,
    "volatility": 8.06,
    "confidence_level": 95
  },
  "real_2025_data": true
}
```

## 📊 **Real Data Integration**

This system uses **actual forward exchange rates** provided by the user for June-September 2025:

### **Data Coverage**
- **Period**: June 16, 2025 - September 1, 2025
- **Currency Pair**: USD/INR
- **Data Points**: 78 daily forward rates
- **Range**: 84.25 - 86.56 INR per USD

### **Data Source Reality**
❌ **No free APIs** provide USD/INR forward rates  
❌ **Forward rates are proprietary** trading data  
✅ **Our solution** uses real user-provided market data  
✅ **Most practical approach** for accurate risk management  

## 🧪 **Testing**

### **Run Component Tests**
```bash
python test_components.py
```

### **Test API Endpoints**
```bash
python test_final_deployment.py
```

### **Expected Results**
- ✅ 78 data points with time-varying forward rates
- ✅ Meaningful P&L calculations (₹12L+ profit on $500k LC)
- ✅ Risk metrics with realistic volatility (8.06%)
- ✅ Interactive charts with real market data

## 🌐 **Deployment**

### **Heroku Deployment**
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main

# Open the app
heroku open
```

### **Environment Variables**
No additional environment variables required. The system uses embedded real forward rates data.

## 📈 **Business Value**

### **For Exporters**
- **Risk Assessment**: Understand currency exposure on LCs
- **Profit Optimization**: Identify optimal settlement dates
- **Decision Support**: Data-driven hedging strategies

### **For Financial Institutions**
- **Portfolio Risk**: Aggregate currency exposure analysis
- **Client Advisory**: Professional risk reports
- **Regulatory Reporting**: VaR and risk metrics

## 🏗️ **Project Structure**

```
Currency_Risk_Management/
├── src/
│   └── currency_risk_mgmt/
│       ├── models/                 # Data models
│       │   └── letter_of_credit.py
│       ├── data_providers/         # Data sources
│       │   ├── forex_provider.py
│       │   ├── forward_rates_provider.py
│       │   └── real_forward_rates_2025.py
│       ├── calculators/            # P&L calculations
│       │   ├── profit_loss.py
│       │   ├── forward_pl_calculator.py
│       │   ├── real_forward_pl_2025.py
│       │   └── risk_metrics.py
│       └── reports/                # Report generation
│           ├── generator.py
│           └── forward_reports.py
├── templates/
│   └── index.html                  # Web interface
├── static/                         # CSS/JS assets
├── tests/                          # Test scripts
├── app.py                          # Main Flask application
├── requirements.txt                # Dependencies
├── Procfile                        # Heroku deployment
├── runtime.txt                     # Python version
└── README.md                       # This file
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Real forward rates data provided by domain expert
- Modern UI inspiration from financial dashboards
- Flask community for excellent documentation
- Chart.js for beautiful data visualization

---

**Built with ❤️ for international trade finance professionals**
