import streamlit as st
import base64
import pandas as pd
from datetime import datetime, timedelta

def account_summary_card(account_name, header_class):
    """Create an account summary card for the dashboard"""
    account = st.session_state.account_info[account_name]
    today_pnl = st.session_state.daily_performance[
        (st.session_state.daily_performance['account'] == account_name) & 
        (st.session_state.daily_performance['date'] == datetime.now().strftime('%Y-%m-%d'))
    ]['pnl'].sum()
    
    week_pnl = st.session_state.daily_performance[
        (st.session_state.daily_performance['account'] == account_name) & 
        (pd.to_datetime(st.session_state.daily_performance['date']) >= 
         pd.to_datetime(datetime.now() - timedelta(days=7)))
    ]['pnl'].sum()
    
    from utils.calculations import calculate_account_metrics
    metrics = calculate_account_metrics(account_name)
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="account-header {header_class}">{account['name']}: {account['strategy']}</div>
            <div style="padding: 1rem;">
                <div>Balance: ${account['current_balance']:,.2f}</div>
                <div>Today: ${today_pnl:+,.2f} ({today_pnl/account['current_balance']*100:+.2f}%)</div>
                <div>Week: ${week_pnl:+,.2f} ({week_pnl/account['current_balance']*100:+.2f}%)</div>
                <div>Win Rate: {metrics['win_rate']*100:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def download_csv(df, filename):
    """Create a download link for a dataframe as CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
    return href