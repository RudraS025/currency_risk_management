# Currency Risk Management System - Complete P&L Guide

## 🎯 Quick Summary: What P&L Means for You

**P&L (Profit & Loss)** shows how currency exchange rate changes affect your money. 

### In Simple Terms:
- **You export goods** → Get paid in USD
- **USD exchange rate changes** → Your INR value changes
- **P&L calculation** → Shows how much you gain/lose

## 📊 Your Current Situation (Live Example)

**Your Paddy Export to Iran:**
- LC Amount: $100,000 USD
- Signed 30 days ago at: ₹85.36 per USD
- Current rate: ₹85.72 per USD
- **Result: You're gaining ₹35,570** (USD got stronger!)

## 🧮 How P&L is Calculated

### The Formula:
```
Current Value = USD Amount × Current Rate
Signing Value = USD Amount × Signing Rate
P&L = Current Value - Signing Value
```

### Your Example:
```
Current Value = $100,000 × 85.72 = ₹85,71,700
Signing Value = $100,000 × 85.36 = ₹85,36,130
P&L = ₹85,71,700 - ₹85,36,130 = +₹35,570
```

## ✅ What Different Results Mean

| P&L Result | What Happened | Impact on You |
|------------|---------------|---------------|
| **Positive (+)** | USD strengthened | You get MORE INR |
| **Negative (-)** | USD weakened | You get LESS INR |
| **Zero (0)** | No change | Same INR value |

## 🚦 Risk Levels

| P&L % | Risk Level | Meaning |
|-------|------------|---------|
| 0-2% | 🟢 LOW | Normal fluctuation |
| 2-5% | 🟡 MEDIUM | Watch closely |
| 5%+ | 🔴 HIGH | Take action |

**Your current risk: 0.42% = LOW RISK** ✅

## 📈 Key Metrics Explained

### 1. Unrealized P&L: ₹35,570
- **What**: Paper profit if you convert today
- **Meaning**: USD strengthened, good for you!

### 2. P&L Percentage: +0.42%
- **What**: Percentage gain on original value
- **Meaning**: Small but favorable movement

### 3. Daily P&L: ₹1,186 per day
- **What**: Average daily impact
- **Meaning**: Low daily volatility

### 4. Days Remaining: 59 days
- **What**: Time left for more changes
- **Meaning**: Still exposed to currency risk

## 🎭 Different Scenarios

### Scenario 1: Favorable (Your Current Situation)
- USD: ₹85.36 → ₹85.72
- P&L: +₹35,570 (Good for you!)
- Action: Consider locking in gains

### Scenario 2: Unfavorable (What Could Happen)
- USD: ₹85.36 → ₹84.50
- P&L: -₹86,130 (Loss for you)
- Action: Hope for recovery or hedge

### Scenario 3: High Volatility
- USD: ₹82.00 → ₹86.00
- P&L: +₹400,000 (Major gain!)
- Action: Definitely lock in gains

## 🛠️ How to Use This Information

### When You Have Positive P&L (Like Now):
1. **Good News**: Currency moved in your favor
2. **Options**: 
   - Wait for more gains
   - Lock in current gains with forward contracts
   - Hedge partially (50-70%)

### When You Have Negative P&L:
1. **Bad News**: Currency moved against you
2. **Options**:
   - Wait for recovery
   - Cut losses by hedging immediately
   - Set stop-loss limits

## 📱 Where to Find P&L in Your System

### 1. **Demo Script** (Live Calculations)
```
python examples\demo_paddy_export.py
```

### 2. **Interactive Calculator** (Test Scenarios)
```
python examples\interactive_pl_calculator.py
```

### 3. **P&L Explanation** (Detailed Breakdown)
```
python examples\pl_explanation.py
```

### 4. **Reports** (Professional Output)
- Excel: `paddy_export_report.xlsx`
- JSON: `paddy_export_report.json`

## 📊 Real Calculation Example

Let's say you want to check a different LC:

```python
# Create your LC
lc = LetterOfCredit(
    lc_id="YOUR-LC-001",
    commodity="Your Product",
    quantity=500,
    unit="tons", 
    rate_per_unit=200,  # $200 per ton = $100,000 total
    currency="USD",
    signing_date="2025-05-01",  # When you signed
    maturity_days=90,
    customer_country="Your Country",
    incoterm="FOB"
)

# Calculate P&L
pl_calculator = ProfitLossCalculator()
result = pl_calculator.calculate_current_pl(lc, "INR")

# Check your result
print(f"Your P&L: ₹{result['unrealized_pl']:,.2f}")
```

## 🔍 Understanding the Code

The P&L calculation happens in:
- **File**: `src/currency_risk_mgmt/calculators/profit_loss.py`
- **Function**: `calculate_current_pl()`
- **Process**: 
  1. Gets historical rate for signing date
  2. Gets current live rate
  3. Calculates INR values
  4. Computes difference = P&L

## 💡 Pro Tips

1. **Monitor Daily**: Check P&L every day
2. **Set Alerts**: Get notified when P&L changes significantly
3. **Track Trends**: Look for patterns in currency movements
4. **Plan Hedging**: Decide in advance when to hedge
5. **Keep Records**: Document all P&L decisions

## ❓ Common Questions

**Q: Why does my P&L change every day?**
A: Exchange rates fluctuate constantly based on market conditions.

**Q: Should I hedge when P&L is positive?**
A: It depends on your risk tolerance. You could lose potential gains but lock in current gains.

**Q: What if I can't get live rates?**
A: The system uses cached rates or estimates, but accuracy may be reduced.

**Q: How accurate are the calculations?**
A: Very accurate for current calculations. Historical rates may have slight variations.

## 🎯 Action Plan Based on Your Current P&L

**Your Current P&L: +₹35,570 (0.42%)**

### Recommendation: MONITOR
- **Risk Level**: LOW ✅
- **Trend**: Favorable ✅
- **Action**: Continue monitoring, consider partial hedging if gains increase

### Next Steps:
1. **Daily Check**: Run the demo script daily
2. **Set Threshold**: Decide at what P&L% you'll hedge
3. **Plan Ahead**: Have hedging strategy ready
4. **Track Performance**: Keep records for future reference

## 📞 Quick Commands to Remember

```bash
# Check your current P&L
python examples\demo_paddy_export.py

# Test different scenarios
python examples\interactive_pl_calculator.py

# Get detailed explanation
python examples\pl_explanation.py

# Create your own LC
python examples\create_your_lc.py
```

---

**Bottom Line**: You're currently in a favorable position with a small gain. The system helps you monitor and make informed decisions about when to lock in gains or wait for better rates. Currency risk management is about making informed choices, not perfect predictions!
