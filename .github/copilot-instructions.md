<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Currency Risk Management System Instructions

This is a Python-based currency risk management system for international trade transactions. When working on this project:

## Key Components
- **Letter of Credit (LC)**: Core financial instrument for international trade
- **Forex Data**: Real-time USD/INR exchange rates and forward rates
- **P&L Calculations**: Profit and loss calculations considering currency fluctuations
- **Risk Analysis**: Currency exposure and risk metrics

## Financial Domain Knowledge
- Use proper financial terminology and calculations
- Consider both spot and forward exchange rates
- Include risk management best practices
- Handle date calculations for LC maturity periods
- Account for business day calculations in forex markets

## Code Standards
- Follow PEP 8 for Python code formatting
- Use type hints for better code documentation
- Implement proper error handling for API calls
- Add comprehensive logging for financial calculations
- Write unit tests for critical financial calculations

## Data Sources
- Primary: Open source forex APIs (yfinance, exchangerate-api)
- Backup sources should be configurable
- Handle API rate limits and failures gracefully
- Cache exchange rate data appropriately

## Security Considerations
- Validate all financial inputs
- Implement proper data sanitization
- Use secure methods for API key management
- Add audit trails for financial calculations
