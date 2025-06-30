"""
Example: Create your own Letter of Credit
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currency_risk_mgmt import LetterOfCredit, ProfitLossCalculator

# Create your LC
my_lc = LetterOfCredit(
    lc_id="LC002_WHEAT_DUBAI",
    commodity="Wheat",
    quantity=500,              # 500 tons
    unit="tons",
    rate_per_unit=350,         # USD 350 per ton
    currency="USD",
    signing_date="2025-07-01", # Tomorrow
    maturity_days=60,          # 2 months
    customer_country="UAE"
)

# Calculate P&L
calculator = ProfitLossCalculator()
pl_result = calculator.calculate_current_pl(my_lc)

print(f"LC: {my_lc}")
print(f"P&L: ₹{pl_result['unrealized_pl']:,.2f}")
