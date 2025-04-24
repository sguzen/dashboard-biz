import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.calculations import calculate_account_metrics, calculate_drawdown
from utils.formatting import account_summary_card

def show():
    """Display the dashboard page"""
    st.title("Trading Tracker Dashboard")
    
    # Account summary cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        account_summary_card("Account 1", "account1-header")
    
    with col2:
        account_summary_card("Account 2", "account2-header")
        
    with col3:
        account_summary_card("Account 3", "account3-header")
    
    # Risk Management Alerts
    st.markdown('<div class="tab-header">Risk Management Alerts</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Calculate drawdown status for each account
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            account = st.session_state.account_info[account_name]
            current_dd, max_dd = calculate_drawdown(account_name)
            
            daily_limit = account['current_balance'] * account['daily_stop']
            pct_of_limit = current_dd / daily_limit if daily_limit > 0 else 0
            
            status_class = "status-ok"
            status_text = "OK"
            
            if pct_of_limit > 0.75:
                status_class = "status-warning"
                status_text = "WARNING"
            elif pct_of_limit > 0.5:
                status_class = "status-caution"
                status_text = "CAUTION"
            
            st.markdown(f"""
                    <div>{account_name}:</div>
                    <div>{pct_of_limit*100:.0f}% of Daily Limit</div>
                    <div class="{status_class}">{status_text}</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Performance Comparison
        metrics_comparison = {}
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            metrics_comparison[account_name] = calculate_account_metrics(account_name)
        
        metrics_df = pd.DataFrame({
            'Metric': ['Win Rate', 'Avg Win (R)', 'Avg Loss (R)', 'Expectancy'],
            'Account 1': [f"{metrics_comparison['Account 1']['win_rate']*100:.1f}%", 
                         f"{metrics_comparison['Account 1']['avg_win']:.2f}", 
                         f"{metrics_comparison['Account 1']['avg_loss']:.2f}", 
                         f"{metrics_comparison['Account 1']['expectancy']:.2f}"],
            'Account 2': [f"{metrics_comparison['Account 2']['win_rate']*100:.1f}%", 
                         f"{metrics_comparison['Account 2']['avg_win']:.2f}", 
                         f"{metrics_comparison['Account 2']['avg_loss']:.2f}", 
                         f"{metrics_comparison['Account 2']['expectancy']:.2f}"],
            'Account 3': [f"{metrics_comparison['Account 3']['win_rate']*100:.1f}%", 
                         f"{metrics_comparison['Account 3']['avg_win']:.2f}", 
                         f"{metrics_comparison['Account 3']['avg_loss']:.2f}", 
                         f"{metrics_comparison['Account 3']['expectancy']:.2f}"]
        })
        
        st.dataframe(metrics_df, use_container_width=True)
    
    # Equity Curve and Recent Trades
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="tab-header">Equity Curve</div>', unsafe_allow_html=True)
        display_equity_curves()
    
    with col2:
        st.markdown('<div class="tab-header">Recent Trades</div>', unsafe_allow_html=True)
        display_recent_trades()

def display_equity_curves():
    """Display equity curves for all accounts"""
    # Create daily equity data
    equity_data = []
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        account_daily = st.session_state.daily_performance[
            st.session_state.daily_performance['account'] == account_name
        ].sort_values('date')
        
        # Calculate cumulative equity
        initial_balance = st.session_state.account_info[account_name]['starting_balance']
        account_daily['equity'] = initial_balance + account_daily['pnl'].cumsum()
        
        for _, row in account_daily.iterrows():
            equity_data.append({
                'Date': row['date'],
                'Account': account_name,
                'Equity': row['equity']
            })
    
    equity_df = pd.DataFrame(equity_data)
    
    # Plot equity curve
    fig = px.line(equity_df, x='Date', y='Equity', color='Account',
                 color_discrete_map={'Account 1': '#34a853', 'Account 2': '#fbbc05', 'Account 3': '#ea4335'})
    fig.update_layout(
        title='Account Equity Curves',
        xaxis_title='Date',
        yaxis_title='Equity ($)',
        legend_title='Account',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def display_recent_trades():
    """Display most recent trades"""
    # Get recent trades
    recent_trades = st.session_state.trade_journal.sort_values('date', ascending=False).head(5)
    
    for _, trade in recent_trades.iterrows():
        card_class = "win-trade" if trade['outcome'] == 'Win' else "loss-trade"
        st.markdown(f"""
            <div class="trade-card {card_class}">
                {trade['date']} - {trade['strategy']} - {trade['outcome']} - ${trade['pnl']}
            </div>
        """, unsafe_allow_html=True)
        
def display_risk_alerts():
    """Display risk alerts with proper contrast"""
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        account = st.session_state.account_info[account_name]
        current_dd, max_dd = calculate_drawdown(account_name)
        
        daily_limit = account['current_balance'] * account['daily_stop']
        pct_of_limit = current_dd / daily_limit if daily_limit > 0 else 0
        
        status_class = "status-ok"
        status_text = "OK"
        
        if pct_of_limit > 0.75:
            status_class = "status-warning"
            status_text = "WARNING"
        elif pct_of_limit > 0.5:
            status_class = "status-caution"
            status_text = "CAUTION"
        
        bg_color = '#f8f9fa' if account_name in ['Account 1', 'Account 3'] else 'white'
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; padding: 0.5rem; background-color: {bg_color};">
                <div class="main-text">{account_name}:</div>
                <div class="main-text">{pct_of_limit*100:.0f}% of Daily Limit</div>
                <div class="{status_class}">{status_text}</div>
            </div>
        """, unsafe_allow_html=True)