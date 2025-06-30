#!/usr/bin/env python3
"""
Interactive P&L Calculator
Test different currency scenarios and understand P&L impact
"""

def calculate_pl_scenario(usd_amount, signing_rate, current_rate, days_elapsed):
    """Calculate P&L for a given scenario"""
    
    # Calculate INR values
    inr_at_signing = usd_amount * signing_rate
    inr_current = usd_amount * current_rate
    
    # Calculate P&L
    unrealized_pl = inr_current - inr_at_signing
    pl_percentage = (unrealized_pl / inr_at_signing) * 100
    daily_pl = unrealized_pl / max(days_elapsed, 1)
    
    # Determine impact
    if unrealized_pl > 0:
        impact = "FAVORABLE - USD strengthened"
        emoji = "✅"
    elif unrealized_pl < 0:
        impact = "UNFAVORABLE - USD weakened"
        emoji = "⚠️"
    else:
        impact = "NEUTRAL - No change"
        emoji = "➡️"
    
    # Determine risk level
    abs_pl_percent = abs(pl_percentage)
    if abs_pl_percent < 2:
        risk_level = "LOW"
    elif abs_pl_percent < 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return {
        'usd_amount': usd_amount,
        'signing_rate': signing_rate,
        'current_rate': current_rate,
        'inr_at_signing': inr_at_signing,
        'inr_current': inr_current,
        'unrealized_pl': unrealized_pl,
        'pl_percentage': pl_percentage,
        'daily_pl': daily_pl,
        'days_elapsed': days_elapsed,
        'impact': impact,
        'emoji': emoji,
        'risk_level': risk_level
    }

def print_scenario_result(result):
    """Print formatted P&L result"""
    
    print(f"\n{'='*60}")
    print(f"P&L CALCULATION RESULT")
    print(f"{'='*60}")
    
    print(f"\n💰 TRANSACTION DETAILS:")
    print(f"   USD Amount: ${result['usd_amount']:,.2f}")
    print(f"   Signing Rate: ₹{result['signing_rate']:.4f} per USD")
    print(f"   Current Rate: ₹{result['current_rate']:.4f} per USD")
    print(f"   Days Elapsed: {result['days_elapsed']} days")
    
    print(f"\n📊 VALUE COMPARISON:")
    print(f"   Value at Signing: ₹{result['inr_at_signing']:,.2f}")
    print(f"   Current Value: ₹{result['inr_current']:,.2f}")
    print(f"   Difference: ₹{result['unrealized_pl']:+,.2f}")
    
    print(f"\n📈 P&L ANALYSIS:")
    print(f"   {result['emoji']} Unrealized P&L: ₹{result['unrealized_pl']:+,.2f}")
    print(f"   {result['emoji']} P&L Percentage: {result['pl_percentage']:+.2f}%")
    print(f"   {result['emoji']} Daily P&L: ₹{result['daily_pl']:+,.2f} per day")
    
    print(f"\n🎯 INTERPRETATION:")
    print(f"   Impact: {result['impact']}")
    print(f"   Risk Level: {result['risk_level']}")
    
    if result['unrealized_pl'] > 0:
        print(f"   📈 You will receive ₹{abs(result['unrealized_pl']):,.2f} MORE when converting USD")
    elif result['unrealized_pl'] < 0:
        print(f"   📉 You will receive ₹{abs(result['unrealized_pl']):,.2f} LESS when converting USD")
    else:
        print(f"   ➡️  No change in INR value")

def interactive_calculator():
    """Interactive P&L calculator"""
    
    print("🧮 INTERACTIVE P&L CALCULATOR")
    print("=" * 40)
    print("Calculate P&L for different currency scenarios")
    print()
    
    while True:
        try:
            print("\nEnter your scenario details:")
            
            # Get user inputs
            usd_amount = float(input("USD Amount (e.g., 100000): $"))
            signing_rate = float(input("Exchange Rate at Signing (e.g., 82.50): ₹"))
            current_rate = float(input("Current Exchange Rate (e.g., 83.25): ₹"))
            days_elapsed = int(input("Days since signing (e.g., 30): "))
            
            # Calculate P&L
            result = calculate_pl_scenario(usd_amount, signing_rate, current_rate, days_elapsed)
            
            # Display result
            print_scenario_result(result)
            
            # Ask if user wants to continue
            continue_calc = input("\nCalculate another scenario? (y/n): ").lower().strip()
            if continue_calc not in ['y', 'yes']:
                break
                
        except ValueError:
            print("❌ Please enter valid numbers!")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def preset_scenarios():
    """Show preset scenarios for common situations"""
    
    print("\n🎭 PRESET SCENARIOS")
    print("=" * 40)
    
    scenarios = [
        {
            'name': 'Small Favorable Movement',
            'usd_amount': 100000,
            'signing_rate': 82.50,
            'current_rate': 82.75,
            'days_elapsed': 15
        },
        {
            'name': 'Large Unfavorable Movement',
            'usd_amount': 50000,
            'signing_rate': 84.00,
            'current_rate': 82.00,
            'days_elapsed': 45
        },
        {
            'name': 'High Volatility Scenario',
            'usd_amount': 200000,
            'signing_rate': 83.00,
            'current_rate': 86.50,
            'days_elapsed': 60
        },
        {
            'name': 'Quick Settlement',
            'usd_amount': 75000,
            'signing_rate': 82.25,
            'current_rate': 82.10,
            'days_elapsed': 7
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        result = calculate_pl_scenario(
            scenario['usd_amount'],
            scenario['signing_rate'],
            scenario['current_rate'],
            scenario['days_elapsed']
        )
        
        print(f"\n📊 Scenario {i}: {scenario['name']}")
        print(f"   ${scenario['usd_amount']:,} USD | ₹{scenario['signing_rate']:.2f} → ₹{scenario['current_rate']:.2f}")
        print(f"   P&L: ₹{result['unrealized_pl']:+,.2f} ({result['pl_percentage']:+.2f}%) | {result['risk_level']} Risk")
        print(f"   {result['impact']}")

if __name__ == "__main__":
    print("💱 CURRENCY P&L CALCULATOR")
    print("=" * 50)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Interactive Calculator")
        print("2. View Preset Scenarios")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            interactive_calculator()
        elif choice == '2':
            preset_scenarios()
        elif choice == '3':
            print("\n👋 Thank you for using the P&L Calculator!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
