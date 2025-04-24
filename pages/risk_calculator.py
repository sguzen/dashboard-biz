import streamlit as st
import pandas as pd
import plotly.express as px
import math
from utils.calculations import calculate_drawdown, calculate_correlation_matrix

def show():
    """Display the risk calculator page"""
    st.title("Risk Calculator")
    
    # Position Size Calculator
    st.markdown('<div class="tab-header">Position Size Calculator</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        calc_account = st.selectbox("Account", ["Account 1", "Account 2", "Account 3"], key="pos_calc_account")
        account_balance = st.session_state.account_info[calc_account]['current_balance']
        st.info(f"Current Balance: ${account_balance:,.2f}")
        
        risk_pct = st.number_input("Risk Per Trade (%)", 
                                 min_value=0.1, max_value=5.0, 
                                 value=st.session_state.account_info[calc_account]['risk_per_trade']*100,
                                 step=0.1,
                                 format="%.1f") / 100
        
        risk_amount = account_balance * risk_pct
        st.info(f"Risk Amount: ${risk_amount:,.2f}")
    
    with col2:
        stop_points = st.number_input("Stop Loss (points)", min_value=0.1, value=12.5, step=0.5)
        point_value = st.number_input("Point Value ($)", min_value=0.1, value=12.50, step=0.1)
        
        if stop_points > 0 and point_value > 0:
            position_size = math.floor(risk_amount / (stop_points * point_value))
            total_risk = position_size * stop_points * point_value
            
            st.success(f"Position Size: {position_size} contracts")
            st.info(f"Actual Risk: ${total_risk:,.2f} ({total_risk/account_balance*100:.2f}%)")
    
    # Drawdown Monitor
    st.markdown('<div class="tab-header">Drawdown Monitor</div>', unsafe_allow_html=True)
    display_drawdown_monitor()
    
    # Recovery Calculator
    st.markdown('<div class="tab-header">Recovery Calculator</div>', unsafe_allow_html=True)
    display_recovery_calculator()
    
    # Correlation Matrix
    st.markdown('<div class="tab-header">Strategy Correlation</div>', unsafe_allow_html=True)
    display_correlation_matrix()

def display_drawdown_monitor():
    """Display drawdown monitor for all accounts"""
    drawdown_data = []
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        account = st.session_state.account_info[account_name]
        current_dd, max_dd = calculate_drawdown(account_name)
        
        daily_limit = account['current_balance'] * account['daily_stop']
        pct_of_limit = current_dd / daily_limit if daily_limit > 0 else 0
        
        if pct_of_limit > 0.75:
            status = "WARNING"
            status_class = "status-warning"
        elif pct_of_limit > 0.5:
            status = "CAUTION"
            status_class = "status-caution"
        else:
            status = "OK"
            status_class = "status-ok"
        
        drawdown_data.append({
            'Account': account_name,
            'Current DD': f"${current_dd:.2f} ({current_dd/account['current_balance']*100:.2f}%)",
            'Daily Limit': f"${daily_limit:.2f} ({account['daily_stop']*100:.1f}%)",
            'Status': f'<div class="{status_class}">{status}</div>',
            'Pct_of_Limit': pct_of_limit
        })
    
    drawdown_df = pd.DataFrame(drawdown_data)
    
    # Sort by percentage of limit (descending)
    drawdown_df = drawdown_df.sort_values('Pct_of_Limit', ascending=False)
    
    # Format the status column without HTML (remove the HTML tags)
    display_df = drawdown_df[['Account', 'Current DD', 'Daily Limit', 'Status']].copy()
    display_df['Status'] = display_df['Status'].str.extract(r'>([A-Z]+)<')
    
    # Display without the hidden column
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def display_recovery_calculator():
    """Display recovery calculator for accounts approaching limits"""
    # Get drawdown data
    drawdown_data = []
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        account = st.session_state.account_info[account_name]
        current_dd, _ = calculate_drawdown(account_name)
        daily_limit = account['current_balance'] * account['daily_stop']
        pct_of_limit = current_dd / daily_limit if daily_limit > 0 else 0
        
        drawdown_data.append({
            'Account': account_name,
            'Pct_of_Limit': pct_of_limit
        })
    
    drawdown_df = pd.DataFrame(drawdown_data)
    
    # Pre-select the account with the highest drawdown percentage
    default_account = drawdown_df.sort_values('Pct_of_Limit', ascending=False).iloc[0]['Account']
    
    col1, col2 = st.columns(2)
    
    with col1:
        recovery_account = st.selectbox("Account", 
                                     ["Account 1", "Account 2", "Account 3"], 
                                     index=["Account 1", "Account 2", "Account 3"].index(default_account),
                                     key="recovery_account")
        
        account = st.session_state.account_info[recovery_account]
        current_dd, _ = calculate_drawdown(recovery_account)
        daily_limit = account['current_balance'] * account['daily_stop']
        
        current_dd_pct = current_dd / account['current_balance'] * 100
        daily_limit_pct = account['daily_stop'] * 100
        pct_of_limit = current_dd / daily_limit if daily_limit > 0 else 0
        
        st.info(f"Current Drawdown: ${current_dd:.2f} ({current_dd_pct:.2f}%)")
        st.info(f"Daily Limit: ${daily_limit:.2f} ({daily_limit_pct:.2f}%)")
        st.info(f"Percentage Used: {pct_of_limit*100:.1f}%")
        
        normal_risk = account['risk_per_trade'] * 100
        st.info(f"Normal Risk Per Trade: {normal_risk:.2f}%")
    
    with col2:
        # Recovery recommendations
        if pct_of_limit > 0.75:
            reduced_risk = normal_risk * 0.5 / 100  # 50% of normal
            st.markdown("""
                <div style="background-color: #fce8e6; padding: 1rem; border-radius: 5px; border-left: 4px solid #ea4335;">
                    <strong>High Risk Warning:</strong>
                    <ul>
                        <li>Reduce position size to 50% of normal</li>
                        <li>Focus only on A+ setups</li>
                        <li>Consider taking a break from trading this account</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        elif pct_of_limit > 0.5:
            reduced_risk = normal_risk * 0.75 / 100  # 75% of normal
            st.markdown("""
                <div style="background-color: #fef7e0; padding: 1rem; border-radius: 5px; border-left: 4px solid #fbbc05;">
                    <strong>Caution:</strong>
                    <ul>
                        <li>Reduce position size to 75% of normal</li>
                        <li>Focus on higher probability setups</li>
                        <li>Avoid correlated trades with other accounts</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        else:
            reduced_risk = normal_risk / 100  # Normal risk
            st.markdown("""
                <div style="background-color: #e6f4ea; padding: 1rem; border-radius: 5px; border-left: 4px solid #34a853;">
                    <strong>Normal Operations:</strong>
                    <ul>
                        <li>Standard position sizing is appropriate</li>
                        <li>Continue with normal risk management</li>
                        <li>No special measures needed</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        reduced_risk_amount = account['current_balance'] * reduced_risk
        st.success(f"Recommended Risk Amount: ${reduced_risk_amount:.2f} ({reduced_risk*100:.2f}% per trade)")

def display_correlation_matrix():
    """Display correlation matrix between strategies"""
    # Calculate correlation matrix
    corr_matrix, avg_correlation = calculate_correlation_matrix()
    
    # Create a heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Strategy Correlation Matrix"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    if avg_correlation < 0.3:
        st.markdown("""
            <div style="background-color: #e6f4ea; padding: 1rem; border-radius: 5px; border-left: 4px solid #34a853;">
                <strong>Low Correlation:</strong> Your strategies show excellent diversification with minimal correlation.
                This separation provides strong risk management benefits.
            </div>
        """, unsafe_allow_html=True)
    elif avg_correlation < 0.6:
        st.markdown("""
            <div style="background-color: #fef7e0; padding: 1rem; border-radius: 5px; border-left: 4px solid #fbbc05;">
                <strong>Moderate Correlation:</strong> Your strategies show some correlation.
                Consider reviewing trade conditions and timing to further reduce correlation.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color: #fce8e6; padding: 1rem; border-radius: 5px; border-left: 4px solid #ea4335;">
                <strong>High Correlation:</strong> Your strategies show significant correlation.
                This reduces the risk management benefits of strategy separation.
                Consider revising your strategies to focus on different market conditions or timeframes.
            </div>
        """, unsafe_allow_html=True)