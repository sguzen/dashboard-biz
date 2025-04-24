import streamlit as st
import pandas as pd
from utils.calculations import calculate_account_metrics, calculate_drawdown
from utils.formatting import download_csv

def show(account_name):
    """Display account-specific page"""
    account = st.session_state.account_info[account_name]
    
    st.title(f"{account_name}: {account['strategy']} Strategy")
    
    # Account Info and Risk Parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="tab-header">Account Information</div>', unsafe_allow_html=True)
        
        info_df = pd.DataFrame({
            'Parameter': ['Starting Balance', 'Current Balance', 'Start Date'],
            'Value': [f"${account['starting_balance']:,.2f}", 
                     f"${account['current_balance']:,.2f}", 
                     account['start_date']]
        })
        
        st.dataframe(info_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown('<div class="tab-header">Risk Parameters</div>', unsafe_allow_html=True)
        
        daily_limit = account['current_balance'] * account['daily_stop']
        weekly_limit = account['current_balance'] * account['weekly_stop']
        risk_per_trade = account['current_balance'] * account['risk_per_trade']
        
        risk_df = pd.DataFrame({
            'Parameter': ['Daily Stop Loss', 'Weekly Stop Loss', 'Risk Per Trade'],
            'Value': [f"{account['daily_stop']*100:.1f}% (${daily_limit:,.2f})", 
                     f"{account['weekly_stop']*100:.1f}% (${weekly_limit:,.2f})", 
                     f"{account['risk_per_trade']*100:.1f}% (${risk_per_trade:,.2f})"]
        })
        
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    # Performance Metrics and Drawdown Tracker
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="tab-header">Performance Metrics</div>', unsafe_allow_html=True)
        display_performance_metrics(account_name)
    
    with col2:
        st.markdown('<div class="tab-header">Drawdown Tracker</div>', unsafe_allow_html=True)
        display_drawdown_tracker(account_name, account)
    
    # Daily Performance Log
    st.markdown('<div class="tab-header">Daily Performance Log</div>', unsafe_allow_html=True)
    display_daily_performance(account_name, account)
    
    # Account-specific trades
    st.markdown('<div class="tab-header">Account Trades</div>', unsafe_allow_html=True)
    display_account_trades(account_name)

def display_performance_metrics(account_name):
    """Display performance metrics for an account"""
    metrics = calculate_account_metrics(account_name)
    
    metrics_df = pd.DataFrame({
        'Metric': ['Win Rate', 'Average Win (R)', 'Average Loss (R)', 'Expectancy', 'Profit Factor'],
        'Value': [f"{metrics['win_rate']*100:.1f}%", 
                 f"{metrics['avg_win']:.2f}", 
                 f"{metrics['avg_loss']:.2f}", 
                 f"{metrics['expectancy']:.2f}", 
                 f"{metrics['profit_factor']:.2f}"]
    })
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

def display_drawdown_tracker(account_name, account):
    """Display drawdown tracker for an account"""
    current_dd, max_dd = calculate_drawdown(account_name)
    daily_limit = account['current_balance'] * account['daily_stop']
    weekly_limit = account['current_balance'] * account['weekly_stop']
    
    daily_remaining = daily_limit - current_dd
    weekly_remaining = weekly_limit - current_dd
    
    recovery_mode = "Yes" if current_dd > daily_limit * 0.75 else "No"
    
    dd_df = pd.DataFrame({
        'Metric': ['Current Drawdown', 'Max Drawdown', 'Daily Remaining', 'Weekly Remaining', 'Recovery Mode'],
        'Value': [f"${current_dd:.2f} ({current_dd/account['current_balance']*100:.2f}%)", 
                 f"${max_dd:.2f} ({max_dd/account['current_balance']*100:.2f}%)", 
                 f"${daily_remaining:.2f} ({daily_remaining/account['current_balance']*100:.2f}%)", 
                 f"${weekly_remaining:.2f} ({weekly_remaining/account['current_balance']*100:.2f}%)", 
                 recovery_mode]
    })
    
    st.dataframe(dd_df, use_container_width=True, hide_index=True)

def display_daily_performance(account_name, account):
    """Display daily performance log for an account"""
    account_daily = st.session_state.daily_performance[
        st.session_state.daily_performance['account'] == account_name
    ].sort_values('date', ascending=False)
    
    account_trades = st.session_state.trade_journal[
        st.session_state.trade_journal['account'] == account_name
    ]
    
    daily_data = []
    for _, day in account_daily.iterrows():
        day_trades = account_trades[account_trades['date'] == day['date']]
        total_trades = len(day_trades)
        win_trades = len(day_trades[day_trades['outcome'] == 'Win'])
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        
        daily_data.append({
            'Date': day['date'],
            'P&L ($)': day['pnl'],
            'P&L (%)': day['pnl'] / account['current_balance'] * 100,
            '# Trades': total_trades,
            'Win Rate': f"{win_rate*100:.1f}%",
            'Notes': ''
        })
    
    daily_df = pd.DataFrame(daily_data)
    st.dataframe(daily_df, use_container_width=True, hide_index=True)

def display_account_trades(account_name):
    """Display trades for a specific account"""
    account_trades = st.session_state.trade_journal[
        st.session_state.trade_journal['account'] == account_name
    ].sort_values('date', ascending=False)
    
    st.dataframe(account_trades[['date', 'time', 'strategy', 'direction', 'pnl', 'r_multiple', 
                               'outcome', 'setup_quality', 'notes']],
               use_container_width=True, hide_index=True)
    
    # Download option
    st.markdown(download_csv(account_trades, f"{account_name}_trades"), unsafe_allow_html=True)