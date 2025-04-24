import streamlit as st
import pandas as pd
import numpy as np
from config import INSTRUMENT_POINT_VALUES

def calculate_account_metrics(account_name):
    """Calculate performance metrics for an account"""
    account_trades = st.session_state.trade_journal[st.session_state.trade_journal['account'] == account_name]
    
    total_trades = len(account_trades)
    win_trades = len(account_trades[account_trades['outcome'] == 'Win'])
    win_rate = win_trades / total_trades if total_trades > 0 else 0
    
    avg_win = account_trades[account_trades['outcome'] == 'Win']['r_multiple'].mean() if win_trades > 0 else 0
    avg_loss = account_trades[account_trades['outcome'] == 'Loss']['r_multiple'].mean() if (total_trades - win_trades) > 0 else 0
    
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss) if total_trades > 0 else 0
    
    win_sum = account_trades[account_trades['pnl'] > 0]['pnl'].sum()
    loss_sum = abs(account_trades[account_trades['pnl'] < 0]['pnl'].sum())
    profit_factor = win_sum / loss_sum if loss_sum > 0 else win_sum
    
    return {
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'expectancy': expectancy,
        'profit_factor': profit_factor
    }

def calculate_drawdown(account_name):
    """Calculate current and maximum drawdown for an account"""
    account_daily = st.session_state.daily_performance[
        st.session_state.daily_performance['account'] == account_name
    ].sort_values('date')
    
    # Calculate cumulative PnL
    account_daily['cum_pnl'] = account_daily['pnl'].cumsum()
    
    # Calculate drawdown
    account_daily['peak'] = account_daily['cum_pnl'].cummax()
    account_daily['drawdown'] = account_daily['peak'] - account_daily['cum_pnl']
    
    current_drawdown = account_daily['drawdown'].iloc[-1] if not account_daily.empty else 0
    max_drawdown = account_daily['drawdown'].max() if not account_daily.empty else 0
    
    return current_drawdown, max_drawdown

def calculate_drawdown_statistics(account_name):
    """Calculate detailed drawdown statistics for an account"""
    account = st.session_state.account_info[account_name]
    strategy = account['strategy']
    
    account_daily = st.session_state.daily_performance[
        st.session_state.daily_performance['account'] == account_name
    ].sort_values('date')
    
    if account_daily.empty:
        return {
            'Strategy': strategy,
            'Max Drawdown': "0.00%",
            'Date': "N/A",
            'Avg Drawdown': "0.00%",
            'Recovery Days': "N/A"
        }
    
    # Calculate cumulative equity and drawdown
    initial_balance = account['starting_balance']
    account_daily['equity'] = initial_balance + account_daily['pnl'].cumsum()
    account_daily['peak'] = account_daily['equity'].cummax()
    account_daily['drawdown'] = account_daily['peak'] - account_daily['equity']
    account_daily['drawdown_pct'] = account_daily['drawdown'] / account_daily['peak'] * 100
    
    # Find max drawdown
    max_dd = account_daily['drawdown_pct'].max()
    max_dd_date = account_daily.loc[account_daily['drawdown_pct'].idxmax(), 'date'] if max_dd > 0 else "N/A"
    
    # Calculate average drawdown
    avg_dd = account_daily['drawdown_pct'].mean()
    
    # Calculate recovery time (days from max drawdown to full recovery)
    recovery_days = "N/A"
    if max_dd > 0:
        max_dd_idx = account_daily['drawdown_pct'].idxmax()
        # Check if drawdown has recovered
        if account_daily.loc[max_dd_idx:, 'drawdown_pct'].min() < 0.1:  # Consider recovered if < 0.1%
            recovered_idx = account_daily.loc[max_dd_idx:].loc[account_daily['drawdown_pct'] < 0.1].index[0]
            recovery_days = recovered_idx - max_dd_idx
        else:
            recovery_days = "Ongoing"
    
    return {
        'Strategy': strategy,
        'Max Drawdown': f"{max_dd:.2f}%",
        'Date': max_dd_date,
        'Avg Drawdown': f"{avg_dd:.2f}%",
        'Recovery Days': recovery_days
    }

def calculate_correlation_matrix():
    """Calculate correlation matrix between strategies"""
    # Calculate PnL by day for each strategy
    strategy_daily = {}
    
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        strategy = st.session_state.account_info[account_name]['strategy']
        account_daily = st.session_state.daily_performance[
            st.session_state.daily_performance['account'] == account_name
        ].sort_values('date')
        
        strategy_daily[strategy] = account_daily[['date', 'pnl']].rename(columns={'pnl': strategy})
    
    # Create a dataframe with all strategies
    corr_data = strategy_daily['Hourly Quarters']
    for strategy in ['930 Strategy', 'Lab Strategy']:
        corr_data = pd.merge(corr_data, strategy_daily[strategy], on='date', how='outer')
    
    # Fill NaN values with 0
    corr_data = corr_data.fillna(0)
    
    # Calculate correlation matrix
    corr_matrix = corr_data[['Hourly Quarters', '930 Strategy', 'Lab Strategy']].corr()
    
    # Calculate average correlation (absolute values)
    hourly_930 = corr_matrix.loc['Hourly Quarters', '930 Strategy']
    hourly_lab = corr_matrix.loc['Hourly Quarters', 'Lab Strategy']
    lab_930 = corr_matrix.loc['Lab Strategy', '930 Strategy']
    
    avg_correlation = (abs(hourly_930) + abs(hourly_lab) + abs(lab_930)) / 3
    
    return corr_matrix, avg_correlation

def calculate_point_value(instrument):
    """Get point value for an instrument"""
    return INSTRUMENT_POINT_VALUES.get(instrument, 50.0)  # Default to ES point value