import os
import pandas as pd
import json
from config import DATA_DIR
from data.sample_data import generate_sample_trades, generate_sample_accounts, generate_sample_performance

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_data(data_type):
    """Load data from storage or generate sample data if files don't exist"""
    if data_type == 'trades':
        file_path = os.path.join(DATA_DIR, 'trades.csv')
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return generate_sample_trades()
        
    elif data_type == 'accounts':
        file_path = os.path.join(DATA_DIR, 'accounts.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return generate_sample_accounts()
        
    elif data_type == 'performance':
        file_path = os.path.join(DATA_DIR, 'performance.csv')
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return generate_sample_performance()
    
    return None

def save_data(data_type, data):
    """Save data to storage files"""
    if data_type == 'trades':
        file_path = os.path.join(DATA_DIR, 'trades.csv')
        data.to_csv(file_path, index=False)
        
    elif data_type == 'accounts':
        file_path = os.path.join(DATA_DIR, 'accounts.json')
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        
    elif data_type == 'performance':
        file_path = os.path.join(DATA_DIR, 'performance.csv')
        data.to_csv(file_path, index=False)