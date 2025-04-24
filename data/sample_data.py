import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import ACCOUNT_CONFIGS

def generate_sample_trades():
    """Generate sample trade data for demonstration"""
    # Create dates for the last 20 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(20)]
    
    # Sample times throughout the day
    times = ['09:30', '10:00', '10:15', '10:30', '11:00', '11:15', 
            '11:30', '11:45', '13:15', '13:30', '14:00', '14:15', 
            '14:30', '14:45', '15:00']
    
    # Create accounts and strategies mapping
    accounts = []
    strategies = []
    for i in range(20):
        # Distribute trades among accounts
        if i % 3 == 0:
            accounts.append('Account 1')
            strategies.append('Hourly Quarters')
        elif i % 3 == 1:
            accounts.append('Account 2')
            strategies.append('930 Strategy')
        else:
            accounts.append('Account 3')
            strategies.append('Lab Strategy')
    
    # Instrument distribution
    instruments = np.random.choice(['ES', 'NQ', 'YM'], size=20)
    
    # Direction distribution
    directions = np.random.choice(['Long', 'Short'], size=20)
    
    # Entry prices based on instruments
    entry_prices = []
    for instrument in instruments:
        if instrument == 'ES':
            entry_prices.append(round(np.random.uniform(4700, 4750), 2))
        elif instrument == 'NQ':
            entry_prices.append(round(np.random.uniform(18300, 18500), 2))
        else:  # YM
            entry_prices.append(round(np.random.uniform(37800, 38000), 2))
    
    # Create exit prices, stop losses, and PnL based on direction and win/loss
    exit_prices = []
    stop_losses = []
    pnls = []
    r_multiples = []
    outcomes = []
    
    for i in range(20):
        # Determine if win or loss (80% win rate for sample data)
        is_win = np.random.choice([True, False], p=[0.8, 0.2])
        outcomes.append('Win' if is_win else 'Loss')
        
        entry = entry_prices[i]
        instrument = instruments[i]
        direction = directions[i]
        
        # Calculate point value
        if instrument == 'ES':
            point_value = 50
        elif instrument == 'NQ':
            point_value = 20
        else:  # YM
            point_value = 5
        
        # Calculate price movements
        if direction == 'Long':
            if is_win:
                # Win for long position
                exit_prices.append(round(entry + np.random.uniform(5, 15), 2))
                stop_losses.append(round(entry - np.random.uniform(10, 25), 2))
            else:
                # Loss for long position
                exit_prices.append(round(entry - np.random.uniform(5, 15), 2))
                stop_losses.append(round(entry - np.random.uniform(20, 30), 2))
        else:  # Short
            if is_win:
                # Win for short position
                exit_prices.append(round(entry - np.random.uniform(5, 15), 2))
                stop_losses.append(round(entry + np.random.uniform(10, 25), 2))
            else:
                # Loss for short position
                exit_prices.append(round(entry + np.random.uniform(5, 15), 2))
                stop_losses.append(round(entry + np.random.uniform(20, 30), 2))
        
        # Calculate position size (between 1-5 contracts)
        position_size = np.random.randint(1, 6)
        
        # Calculate P&L based on price difference and position size
        if direction == 'Long':
            pnl = (exit_prices[i] - entry) * position_size * point_value
            if stop_losses[i] < entry:  # Valid stop for long
                r_multiple = (exit_prices[i] - entry) / (entry - stop_losses[i])
            else:
                r_multiple = 0  # Invalid stop, just for safety
        else:  # Short
            pnl = (entry - exit_prices[i]) * position_size * point_value
            if stop_losses[i] > entry:  # Valid stop for short
                r_multiple = (entry - exit_prices[i]) / (stop_losses[i] - entry)
            else:
                r_multiple = 0  # Invalid stop, just for safety
        
        pnls.append(round(pnl, 2))
        r_multiples.append(round(r_multiple, 2))
    
    # Setup quality (higher for wins, lower for losses)
    setup_qualities = []
    for outcome in outcomes:
        if outcome == 'Win':
            setup_qualities.append(np.random.choice([3, 4, 5], p=[0.2, 0.3, 0.5]))
        else:
            setup_qualities.append(np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3]))
    
    # Execution quality (similar to setup quality)
    execution_qualities = []
    for outcome in outcomes:
        if outcome == 'Win':
            execution_qualities.append(np.random.choice([3, 4, 5], p=[0.2, 0.3, 0.5]))
        else:
            execution_qualities.append(np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3]))
    
    # Trade notes
    # Trade notes
    notes_options = [
        'Perfect setup', 'Gap fade', 'Trend continuation', 'Support bounce', 
        'Resistance rejection', 'VWAP fade', 'Failed breakout', 'Double top',
        'Double bottom', 'Key level test', 'Reversal pattern', 'Momentum trade',
        'News reaction', 'Range breakout', 'Trend reversal'
    ]
    notes = np.random.choice(notes_options, size=20)
    
    # Create DataFrame
    trade_data = pd.DataFrame({
        'date': np.random.choice(dates, size=20),
        'time': np.random.choice(times, size=20),
        'account': accounts,
        'strategy': strategies,
        'instrument': instruments,
        'direction': directions,
        'entry_price': entry_prices,
        'exit_price': exit_prices,
        'stop_loss': stop_losses,
        'position_size': np.random.randint(1, 6, size=20),
        'pnl': pnls,
        'r_multiple': r_multiples,
        'outcome': outcomes,
        'setup_quality': setup_qualities,
        'execution_quality': execution_qualities,
        'notes': notes
    })
    
    # Sort by date (newest first)
    trade_data = trade_data.sort_values('date', ascending=False)
    
    return trade_data

def generate_sample_accounts():
    """Generate sample account data for demonstration"""
    # Start with the config values
    account_info = ACCOUNT_CONFIGS.copy()
    
    # Add current balance (slightly different from starting balance to show P&L)
    account_info['Account 1']['current_balance'] = 147250
    account_info['Account 2']['current_balance'] = 151320
    account_info['Account 3']['current_balance'] = 98750
    
    # Add start dates
    account_info['Account 1']['start_date'] = '2025-01-15'
    account_info['Account 2']['start_date'] = '2025-01-15'
    account_info['Account 3']['start_date'] = '2025-02-01'
    
    return account_info

def generate_sample_performance():
    """Generate sample daily performance data for demonstration"""
    # Create dates for the last 30 days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # Generate random P&L for each account
    account1_pnl = []
    account2_pnl = []
    account3_pnl = []
    
    for _ in range(30):
        # Account 1: Hourly Quarters - consistent, smaller P&L
        account1_pnl.append(round(np.random.normal(400, 300), 2))
        
        # Account 2: 930 Strategy - similar profile to Account 1
        account2_pnl.append(round(np.random.normal(350, 250), 2))
        
        # Account 3: Lab Strategy - higher volatility, larger swings
        account3_pnl.append(round(np.random.normal(300, 500), 2))
    
    # Create DataFrame
    daily_performance = pd.DataFrame({
        'date': dates * 3,
        'account': ['Account 1'] * 30 + ['Account 2'] * 30 + ['Account 3'] * 30,
        'pnl': account1_pnl + account2_pnl + account3_pnl
    })
    
    return daily_performance