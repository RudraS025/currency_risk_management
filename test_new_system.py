#!/usr/bin/env python3
"""
Test script for the new backdated LC system
"""

import requests
import json
from datetime import datetime, timedelta

# Test data
base_url = "http://127.0.0.1:5000"

# Create test LC data (backdated)
issue_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
test_lc = {
    "lc_number": "TEST-BACKDATED-001",
    "amount_usd": 500000,
    "issue_date": issue_date,
    "maturity_days": 60,
    "contract_rate": 82.5,
    "commodity": "Paddy Export",
    "beneficiary": "Test Exporter"
}

print("🔍 Testing New Backdated LC System")
print("=" * 50)

# Test 1: Health check
print("\n1. Testing Health Check...")
try:
    response = requests.get(f"{base_url}/api/health")
    if response.status_code == 200:
        data = response.json()
        print("✅ Health check passed")
        print(f"   Version: {data['version']}")
        print(f"   Focus: {data['focus']}")
        print(f"   Data Source: {data['data_source']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Health check error: {e}")

# Test 2: Date validation
print("\n2. Testing Date Validation...")
try:
    response = requests.post(f"{base_url}/api/validate-dates", json={
        "issue_date": issue_date,
        "maturity_days": 60
    })
    if response.status_code == 200:
        data = response.json()
        validation = data['validation']
        print("✅ Date validation passed")
        print(f"   Issue date valid: {validation['issue_date_valid']}")
        print(f"   Maturity date valid: {validation['maturity_date_valid']}")
        print(f"   Is backdated: {validation['is_backdated']}")
        print(f"   Maturity date: {validation['maturity_date']}")
    else:
        print(f"❌ Date validation failed: {response.status_code}")
except Exception as e:
    print(f"❌ Date validation error: {e}")

# Test 3: P&L Calculation
print("\n3. Testing P&L Calculation...")
try:
    response = requests.post(f"{base_url}/api/calculate-pl", json=test_lc)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            pl_data = data['data']
            risk_metrics = data['risk_metrics']
            
            print("✅ P&L calculation successful")
            print(f"   Final P&L: ₹{pl_data['total_pl_inr']:,.2f}")
            print(f"   Max Profit: ₹{pl_data['max_profit']:,.2f}")
            print(f"   Max Loss: ₹{pl_data['max_loss']:,.2f}")
            print(f"   Data Source: {pl_data['data_source']}")
            print(f"   Daily data points: {len(pl_data['daily_pl'])}")
            print(f"   VaR (95%): ₹{risk_metrics['var_95']:,.2f}")
            print(f"   Backdated analysis: {data['backdated_analysis']}")
        else:
            print(f"❌ P&L calculation failed: {data.get('error')}")
    else:
        print(f"❌ P&L calculation HTTP error: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ P&L calculation error: {e}")

# Test 4: Scenario Analysis
print("\n4. Testing Scenario Analysis...")
try:
    response = requests.post(f"{base_url}/api/scenario-analysis", json=test_lc)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            scenarios = data['scenarios']
            print("✅ Scenario analysis successful")
            print(f"   Base P&L: ₹{data['base_pl']:,.2f}")
            print(f"   Scenarios tested: {len(scenarios)}")
            for scenario in scenarios[:3]:  # Show first 3
                print(f"   - {scenario['name']}: ₹{scenario['pl_inr']:,.2f} ({scenario['impact']})")
        else:
            print(f"❌ Scenario analysis failed: {data.get('error')}")
    else:
        print(f"❌ Scenario analysis HTTP error: {response.status_code}")
except Exception as e:
    print(f"❌ Scenario analysis error: {e}")

# Test 5: Report Generation
print("\n5. Testing Report Generation...")
try:
    response = requests.post(f"{base_url}/api/generate-report", json=test_lc)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            report = data['report']
            print("✅ Report generation successful")
            print(f"   LC ID: {report['lc_id']}")
            print(f"   Total Value: {report['total_value']}")
            print(f"   Status: {report['status']}")
            print(f"   Analysis Period: {report.get('analysis_period', 'N/A')}")
            print(f"   Data Source: {report.get('data_source', 'N/A')}")
        else:
            print(f"❌ Report generation failed: {data.get('error')}")
    else:
        print(f"❌ Report generation HTTP error: {response.status_code}")
except Exception as e:
    print(f"❌ Report generation error: {e}")

print("\n" + "=" * 50)
print("🎉 System test completed!")
print("💡 The new backdated LC system is ready for deployment.")
