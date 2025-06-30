# Currency Risk Management System - P&L Calculations Explained

## Overview
The Profit & Loss (P&L) calculation is the heart of currency risk management. It shows how exchange rate movements affect the value of your international trade transactions.

## What is P&L in Currency Risk?

When you export goods and receive payment in foreign currency (like USD), you face **currency risk**. The value of that foreign currency can change between:
- **Signing Date**: When you sign the Letter of Credit
- **Current Date**: Today's exchange rate
- **Maturity Date**: When you actually receive the payment

## P&L Calculation Formula

### Basic Formula:
```
Unrealized P&L = (Current Exchange Rate - Signing Exchange Rate) × USD Amount

P&L Percentage = (Unrealized P&L ÷ Value at Signing) × 100

Daily P&L = Unrealized P&L ÷ Days Elapsed
```

### Step-by-Step Process:

1. **Get Signing Rate**: Exchange rate when LC was signed
2. **Get Current Rate**: Today's exchange rate
3. **Calculate INR Values**:
   - Value at Signing = USD Amount × Signing Rate
   - Current Value = USD Amount × Current Rate
4. **Calculate P&L**: Current Value - Signing Value

## Real Example from the System

From our live calculation:
- **LC Amount**: $100,000 USD
- **Signing Rate**: ₹85.3613 per USD (30 days ago)
- **Current Rate**: ₹85.7170 per USD (today)

### Calculations:
- **Value at Signing**: $100,000 × 85.3613 = ₹8,536,129.76
- **Current Value**: $100,000 × 85.7170 = ₹8,571,700.29
- **Unrealized P&L**: ₹8,571,700.29 - ₹8,536,129.76 = **₹35,570.53**
- **P&L Percentage**: (₹35,570.53 ÷ ₹8,536,129.76) × 100 = **0.42%**
- **Daily P&L**: ₹35,570.53 ÷ 30 days = **₹1,185.68 per day**

## What Different P&L Results Mean

### ✅ Positive P&L (Favorable)
- **Meaning**: USD has strengthened against INR
- **Impact**: You will receive MORE INR when converting USD
- **Example**: If USD goes from ₹82.50 to ₹83.25, you gain ₹75,000 on $100,000

### ⚠️ Negative P&L (Unfavorable)
- **Meaning**: USD has weakened against INR
- **Impact**: You will receive LESS INR when converting USD
- **Example**: If USD goes from ₹82.50 to ₹81.75, you lose ₹75,000 on $100,000

### ➡️ Zero P&L (Neutral)
- **Meaning**: Exchange rate hasn't changed
- **Impact**: No currency impact on your transaction

## Risk Levels

The system categorizes risk based on P&L percentage:

| P&L % Range | Risk Level | Meaning |
|-------------|------------|---------|
| 0% to ±2% | LOW | Normal market fluctuation |
| ±2% to ±5% | MEDIUM | Moderate currency movement |
| Above ±5% | HIGH | Significant currency volatility |

## Key Metrics Explained

### 1. Unrealized P&L
- **What**: The paper profit/loss if you converted today
- **Why Important**: Shows current currency impact
- **Example**: ₹35,570.53 gain means USD strengthened

### 2. P&L Percentage
- **What**: P&L as percentage of original value
- **Why Important**: Shows relative impact size
- **Example**: 0.42% is a small favorable movement

### 3. Daily P&L
- **What**: Average P&L per day since signing
- **Why Important**: Shows daily volatility
- **Example**: ₹1,185.68 per day average movement

### 4. Days Remaining
- **What**: Days until LC maturity
- **Why Important**: Shows remaining exposure period
- **Example**: 59 days of continued currency risk

## How to Use This Information

### For Exporters (Receiving USD):
- **Positive P&L**: Good news! USD strengthened, you'll get more INR
- **Negative P&L**: Consider hedging strategies to lock in rates
- **High Daily P&L**: High volatility, consider immediate action

### For Importers (Paying USD):
- **Positive P&L**: Bad news! USD strengthened, you'll pay more INR
- **Negative P&L**: Good news! USD weakened, you'll pay less INR
- **High Daily P&L**: High volatility, consider hedging

## Hedging Strategies Based on P&L

### When P&L is Positive (Favorable):
1. **Lock in Gains**: Use forward contracts to secure favorable rate
2. **Partial Hedging**: Hedge 50-70% to capture some gains while keeping upside
3. **Monitor Closely**: Daily monitoring if trend continues

### When P&L is Negative (Unfavorable):
1. **Wait and Watch**: Hope for recovery if trend is temporary
2. **Cut Losses**: Hedge immediately if trend looks permanent
3. **Diversify**: Spread risk across multiple currencies/time periods

## Where to Find P&L in the System

### 1. Live Calculation
```python
from currency_risk_mgmt.calculators.profit_loss import ProfitLossCalculator

pl_calculator = ProfitLossCalculator()
pl_result = pl_calculator.calculate_current_pl(lc, "INR")
```

### 2. Reports
- **Excel Report**: `paddy_export_report.xlsx` - P&L Summary tab
- **JSON Report**: `paddy_export_report.json` - pl_analysis section
- **Visualizations**: Charts showing P&L trends over time

### 3. Demo Scripts
- `examples/demo_paddy_export.py` - Full P&L analysis
- `examples/pl_explanation.py` - Detailed P&L breakdown
- `examples/create_your_lc.py` - Calculate P&L for your own LC

## Advanced P&L Features

### 1. Forward P&L Projection
Estimates P&L at maturity using forward rates:
```python
forward_pl = pl_calculator.calculate_forward_pl_projection(lc, "INR")
```

### 2. Scenario Analysis
Tests P&L under different exchange rate scenarios:
```python
scenarios = pl_calculator.calculate_scenario_analysis(lc, "INR", rate_changes)
```

### 3. Historical P&L Tracking
Tracks P&L changes over time for trend analysis.

## Best Practices

1. **Daily Monitoring**: Check P&L daily for active LCs
2. **Set Alerts**: Define P&L thresholds for automatic notifications
3. **Document Decisions**: Keep records of why you hedged or didn't hedge
4. **Review Regularly**: Analyze P&L patterns to improve future decisions
5. **Use Multiple Metrics**: Don't rely on just P&L %, consider daily volatility too

## Common Questions

### Q: Why does P&L change daily?
**A**: Exchange rates fluctuate constantly based on market conditions, economic news, and global events.

### Q: Should I hedge when P&L is positive?
**A**: It depends on your risk tolerance and market outlook. Positive P&L could increase further, or reverse.

### Q: What if I can't get historical rates?
**A**: The system uses current rates as fallback, but accuracy may be reduced for older LCs.

### Q: How accurate are the calculations?
**A**: Very accurate for current rates. Historical rates depend on data availability and may have slight variations.

## Summary

P&L calculation helps you:
1. **Understand** currency impact on your transactions
2. **Quantify** risk in monetary terms
3. **Make informed** hedging decisions
4. **Track performance** over time
5. **Plan** for future currency movements

The system automatically handles all calculations and provides actionable insights to help you manage currency risk effectively.
