#!/usr/bin/env python3
import yfinance as yf
import pandas as pd

print('Testing Yahoo Finance USD/INR data...')

try:
    ticker = yf.Ticker('USDINR=X')
    data = ticker.history(period='5d')
    print(f'Data shape: {data.shape}')
    
    if not data.empty:
        latest_rate = data['Close'].iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        print(f'Latest rate: ₹{latest_rate:.4f}')
        print(f'Latest date: {latest_date}')
        print('✅ Real USD/INR data available!')
    else:
        print('❌ No data available')
        
except Exception as e:
    print(f'❌ Error: {e}')
