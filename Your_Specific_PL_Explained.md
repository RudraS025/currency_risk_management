# Your Specific P&L Calculation - Detailed Explanation

## 📊 Your Exact Values Explained

The values you mentioned are from your live Currency Risk Management System:

```
Original Value (at signing): ₹34,499,679.57
Current Value (today): ₹34,286,801.15
Unrealized Loss: ₹-212,878.42 (-0.62%)
Daily Loss: ₹-15,205.60
```

## 🔢 Complete Breakdown

### Transaction Details:
- **LC Amount**: $400,000 USD (Paddy export to Iran)
- **Signing Date**: ~June 16, 2025 (14 days ago)
- **Calculation Date**: June 30, 2025 (Today)
- **Days Elapsed**: 14 days

### Exchange Rates:
- **Rate at Signing**: ₹86.2492 per USD
- **Current Rate**: ₹85.7170 per USD
- **Rate Change**: -₹0.5322 (-0.62%)

## 🧮 Step-by-Step Calculation

### 1. Original Value Calculation:
```
Original Value = USD Amount × Signing Rate
₹34,499,679.57 = $400,000 × ₹86.2492
```

### 2. Current Value Calculation:
```
Current Value = USD Amount × Current Rate
₹34,286,801.15 = $400,000 × ₹85.7170
```

### 3. Unrealized Loss Calculation:
```
Unrealized Loss = Current Value - Original Value
₹-212,878.42 = ₹34,286,801.15 - ₹34,499,679.57
```

### 4. P&L Percentage Calculation:
```
P&L % = (Unrealized Loss ÷ Original Value) × 100
-0.62% = (₹-212,878.42 ÷ ₹34,499,679.57) × 100
```

### 5. Daily Loss Calculation:
```
Daily Loss = Unrealized Loss ÷ Days Elapsed
₹-15,205.60 = ₹-212,878.42 ÷ 14 days
```

## 📅 Timeline Analysis

| Date | Event | USD/INR Rate | Value in INR |
|------|-------|--------------|--------------|
| **June 16, 2025** | LC Signed | ₹86.2492 | ₹34,499,679.57 |
| **June 30, 2025** | Today | ₹85.7170 | ₹34,286,801.15 |
| **Difference** | 14 days | -₹0.5322 | **-₹212,878.42** |

## 🎯 What This Means for Your Business

### Currency Movement:
- **USD has WEAKENED** against INR by 0.62%
- You signed when $1 = ₹86.25
- Today $1 = ₹85.72
- **You're getting less INR for the same USD**

### Financial Impact:
- **Expected Amount**: ₹3.45 crores (at signing)
- **Current Worth**: ₹3.43 crores (today)
- **Loss**: ₹2.13 lakhs due to currency movement
- **Daily Impact**: Losing ₹15,206 per day on average

### Risk Assessment:
- **Risk Level**: LOW (only 0.62% movement)
- **Trend**: Unfavorable (USD weakening)
- **Time Factor**: 14 days active, more time for recovery

## 📊 Data Source Information

This calculation is based on:
- **Current Rate Source**: Yahoo Finance API
- **Rate Fetched**: June 30, 2025
- **Confidence Level**: 60% (due to some API limitations)
- **Update Frequency**: Live/Real-time

## 🔍 Verification

All your values are mathematically correct:
- ✅ Original Value: ₹34,499,679.57
- ✅ Current Value: ₹34,286,801.15  
- ✅ Unrealized Loss: ₹-212,878.42
- ✅ P&L Percentage: -0.62%
- ✅ Daily Loss: ₹-15,205.60

## 💡 Key Insights

1. **"Unrealized" Loss**: This is a paper loss - you only lose this money if you convert USD to INR today
2. **Daily Trend**: You're losing about ₹15K per day due to currency movement
3. **Small Movement**: 0.62% is a relatively small currency fluctuation
4. **Recovery Potential**: USD could strengthen again, reducing or eliminating the loss
5. **Time Factor**: You have 75 days until LC maturity for potential recovery

## 🎯 Business Implications

### If USD continues to weaken:
- Your loss will increase
- Consider hedging to prevent further losses
- Monitor daily for trend changes

### If USD recovers:
- Your loss will decrease or turn into profit
- You might want to wait for better rates
- Set target rates for decision making

### Current Recommendation:
- **MONITOR CLOSELY** - Loss is manageable but trending unfavorably
- **SET ALERTS** - Get notified if loss increases significantly
- **PREPARE STRATEGY** - Decide at what loss level you'll hedge

## 📞 How to Track This

Run these commands to monitor your P&L:

```bash
# Check current P&L
python examples\demo_paddy_export.py

# View detailed breakdown
python examples\specific_pl_breakdown.py

# Test different scenarios
python examples\interactive_pl_calculator.py
```

The system will show updated values each time you run it, helping you track whether your situation is improving or worsening.
