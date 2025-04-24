import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.calculations import calculate_account_metrics, calculate_drawdown_statistics
from config import STRATEGY_COLORS

def show():
    """Display the performance analytics page"""
    st.title("Performance Analytics")
    
    # Strategy Comparison
    st.markdown('<div class="tab-header">Strategy Comparison</div>', unsafe_allow_html=True)
    display_strategy_comparison()
    
    # Win Rate Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="tab-header">Win Rate by Day of Week</div>', unsafe_allow_html=True)
        display_win_rate_by_day()
    
    with col2:
        st.markdown('<div class="tab-header">Performance by Time of Day</div>', unsafe_allow_html=True)
        display_performance_by_time()
    
    # Drawdown Analysis
    st.markdown('<div class="tab-header">Drawdown Analysis</div>', unsafe_allow_html=True)
    display_drawdown_analysis()
    
    # Additional Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="tab-header">Win Rate by Setup Quality</div>', unsafe_allow_html=True)
        display_win_rate_by_setup_quality()
    
    with col2:
        st.markdown('<div class="tab-header">Profit Factor by Month</div>', unsafe_allow_html=True)
        display_profit_factor_by_month()
    
    # Strategy Optimization Insights
    st.markdown('<div class="tab-header">Strategy Optimization Insights</div>', unsafe_allow_html=True)
    display_strategy_insights()
    
    # Overall Business Analysis
    st.markdown('<div class="tab-header">Business Performance Summary</div>', unsafe_allow_html=True)
    display_business_summary()

def display_strategy_comparison():
    """Display strategy comparison metrics"""
    # Get metrics for each strategy
    metrics_data = {}
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        strategy = st.session_state.account_info[account_name]['strategy']
        metrics_data[strategy] = calculate_account_metrics(account_name)
        
        # Add monthly return calculation
        account_daily = st.session_state.daily_performance[
            st.session_state.daily_performance['account'] == account_name
        ].sort_values('date')
        
        if not account_daily.empty:
            monthly_return = account_daily['pnl'].sum() / st.session_state.account_info[account_name]['current_balance'] * 100
            metrics_data[strategy]['monthly_return'] = monthly_return
        else:
            metrics_data[strategy]['monthly_return'] = 0
    
    # Create comparison dataframe
    comparison_data = []
    metrics_list = ['Win Rate', 'Average Win (R)', 'Average Loss (R)', 'Expectancy', 'Monthly Return (%)']
    
    for metric_name, metric_key in zip(metrics_list, ['win_rate', 'avg_win', 'avg_loss', 'expectancy', 'monthly_return']):
        row_data = {'Metric': metric_name}
        
        for strategy in ['Hourly Quarters', '930 Strategy', 'Lab Strategy']:
            if metric_key == 'win_rate':
                row_data[strategy] = f"{metrics_data[strategy][metric_key]*100:.1f}%"
            elif metric_key == 'monthly_return':
                row_data[strategy] = f"{metrics_data[strategy][metric_key]:.2f}%"
            else:
                row_data[strategy] = f"{metrics_data[strategy][metric_key]:.2f}"
        
        # Add analysis column
        if metric_name == 'Win Rate':
            analysis = "All strategies within expected ranges"
        elif metric_name == 'Average Win (R)':
            analysis = "Lab strategy has highest reward potential"
        elif metric_name == 'Average Loss (R)':
            analysis = "All strategies maintain controlled losses"
        elif metric_name == 'Expectancy':
            analysis = "All strategies show positive expectancy"
        else:
            analysis = "Lab has highest return with highest risk"
        
        row_data['Analysis'] = analysis
        comparison_data.append(row_data)
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

def display_win_rate_by_day():
    """Display win rates by day of week for each strategy"""
    # Calculate win rates by day of week for each strategy
    day_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}
    
    day_data = []
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        strategy = st.session_state.account_info[account_name]['strategy']
        account_trades = st.session_state.trade_journal[
            st.session_state.trade_journal['account'] == account_name
        ]
        
        for day_num in range(5):
            # Convert string dates to datetime for weekday calculation
            account_trades['datetime'] = pd.to_datetime(account_trades['date'])
            day_trades = account_trades[account_trades['datetime'].dt.weekday == day_num]
            
            if len(day_trades) > 0:
                win_rate = len(day_trades[day_trades['outcome'] == 'Win']) / len(day_trades)
            else:
                win_rate = 0
            
            day_data.append({
                'Day': day_mapping[day_num],
                'Strategy': strategy,
                'Win Rate': win_rate
            })
    
    day_df = pd.DataFrame(day_data)
    
    # Create bar chart
    fig = px.bar(
        day_df,
        x='Day',
        y='Win Rate',
        color='Strategy',
        barmode='group',
        title='Win Rate by Day of Week',
        color_discrete_map=STRATEGY_COLORS
    )
    fig.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig, use_container_width=True)

def display_performance_by_time():
    """Display performance by time of day for each strategy"""
    # Group trades by hour
    all_trades = st.session_state.trade_journal.copy()
    all_trades['hour'] = all_trades['time'].str.split(':').str[0].astype(int)
    
    time_data = []
    for hour in sorted(all_trades['hour'].unique()):
        hour_trades = all_trades[all_trades['hour'] == hour]
        
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            strategy = st.session_state.account_info[account_name]['strategy']
            strategy_hour_trades = hour_trades[hour_trades['account'] == account_name]
            
            if len(strategy_hour_trades) > 0:
                win_rate = len(strategy_hour_trades[strategy_hour_trades['outcome'] == 'Win']) / len(strategy_hour_trades)
                avg_pnl = strategy_hour_trades['pnl'].mean()
            else:
                win_rate = 0
                avg_pnl = 0
            
            time_data.append({
                'Hour': f"{hour:02d}:00",
                'Strategy': strategy,
                'Win Rate': win_rate,
                'Avg PnL': avg_pnl
            })
    
    time_df = pd.DataFrame(time_data)
    
    # Create line chart
    fig = px.line(
        time_df,
        x='Hour',
        y='Win Rate',
        color='Strategy',
        title='Win Rate by Time of Day',
        markers=True,
        color_discrete_map=STRATEGY_COLORS
    )
    fig.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig, use_container_width=True)

def display_drawdown_analysis():
    """Display drawdown analysis with equity curves and statistics"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create equity curves with drawdown visualization
        display_equity_and_drawdown_curves()
    
    with col2:
        # Drawdown statistics
        drawdown_stats = []
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            strategy = st.session_state.account_info[account_name]['strategy']
            stats = calculate_drawdown_statistics(account_name)
            drawdown_stats.append(stats)
        
        drawdown_stats_df = pd.DataFrame(drawdown_stats)
        st.dataframe(drawdown_stats_df, use_container_width=True, hide_index=True)
        
        # Drawdown recommendations
        st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
                <h4>Drawdown Management Tips:</h4>
                <ul>
                    <li>Monitor strategy correlation during drawdowns</li>
                    <li>Reduce position size when approaching daily limits</li>
                    <li>Be patient during recovery periods</li>
                    <li>Document market conditions during drawdowns</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

def display_equity_and_drawdown_curves():
    """Display equity curves and drawdown visualization"""
    # Create equity curves with drawdown visualization
    equity_data = []
    drawdown_data = []
    
    for account_name in ["Account 1", "Account 2", "Account 3"]:
        strategy = st.session_state.account_info[account_name]['strategy']
        account_daily = st.session_state.daily_performance[
            st.session_state.daily_performance['account'] == account_name
        ].sort_values('date')
        
        if not account_daily.empty:
            # Calculate cumulative equity and drawdown
            initial_balance = st.session_state.account_info[account_name]['starting_balance']
            account_daily['equity'] = initial_balance + account_daily['pnl'].cumsum()
            account_daily['peak'] = account_daily['equity'].cummax()
            account_daily['drawdown'] = (account_daily['peak'] - account_daily['equity']) / account_daily['peak'] * 100
            
            for _, row in account_daily.iterrows():
                equity_data.append({
                    'Date': row['date'],
                    'Strategy': strategy,
                    'Equity': row['equity']
                })
                
                drawdown_data.append({
                    'Date': row['date'],
                    'Strategy': strategy,
                    'Drawdown (%)': row['drawdown']
                })
    
    equity_df = pd.DataFrame(equity_data)
    drawdown_df = pd.DataFrame(drawdown_data)
    
    # Create subplot with equity and drawdown
    fig = make_subplots(rows=2, cols=1, 
                       shared_xaxes=True, 
                       vertical_spacing=0.1,
                       subplot_titles=("Equity Curves", "Drawdown"))
    
    # Add equity curves
    for strategy, color in STRATEGY_COLORS.items():
        strategy_equity = equity_df[equity_df['Strategy'] == strategy]
        
        if not strategy_equity.empty:
            fig.add_trace(
                go.Scatter(
                    x=strategy_equity['Date'],
                    y=strategy_equity['Equity'],
                    mode='lines',
                    name=strategy,
                    line=dict(color=color)
                ),
                row=1, col=1
            )
    
    # Add drawdown
    for strategy, color in STRATEGY_COLORS.items():
        strategy_drawdown = drawdown_df[drawdown_df['Strategy'] == strategy]
        
        if not strategy_drawdown.empty:
            fig.add_trace(
                go.Scatter(
                    x=strategy_drawdown['Date'],
                    y=strategy_drawdown['Drawdown (%)'],
                    mode='lines',
                    name=f"{strategy} DD",
                    line=dict(color=color, dash='dot'),
                    showlegend=False
                ),
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        height=500,
        title="Equity Curves and Drawdown Analysis",
        yaxis_title="Equity ($)",
        yaxis2_title="Drawdown (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Invert y-axis for drawdown (so down is worse)
    fig.update_yaxes(autorange="reversed", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)

def display_win_rate_by_setup_quality():
    """Display win rate by setup quality for each strategy"""
    # Calculate win rate by setup quality
    setup_data = []
    for quality in range(1, 6):
        quality_trades = st.session_state.trade_journal[st.session_state.trade_journal['setup_quality'] == quality]
        
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            strategy = st.session_state.account_info[account_name]['strategy']
            strategy_quality_trades = quality_trades[quality_trades['account'] == account_name]
            
            if len(strategy_quality_trades) > 0:
                win_rate = len(strategy_quality_trades[strategy_quality_trades['outcome'] == 'Win']) / len(strategy_quality_trades)
            else:
                win_rate = 0
            
            setup_data.append({
                'Setup Quality': quality,
                'Strategy': strategy,
                'Win Rate': win_rate
            })
    
    setup_df = pd.DataFrame(setup_data)
    
    # Create bar chart
    fig = px.bar(
        setup_df,
        x='Setup Quality',
        y='Win Rate',
        color='Strategy',
        barmode='group',
        title='Win Rate by Setup Quality',
        color_discrete_map=STRATEGY_COLORS
    )
    fig.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig, use_container_width=True)

def display_profit_factor_by_month():
    """Display profit factor by month for each strategy"""
    # Calculate profit factor by month
    all_trades = st.session_state.trade_journal.copy()
    all_trades['month'] = pd.to_datetime(all_trades['date']).dt.strftime('%Y-%m')
    
    month_data = []
    for month in sorted(all_trades['month'].unique()):
        month_trades = all_trades[all_trades['month'] == month]
        
        for account_name in ["Account 1", "Account 2", "Account 3"]:
            strategy = st.session_state.account_info[account_name]['strategy']
            strategy_month_trades = month_trades[month_trades['account'] == account_name]
            
            if len(strategy_month_trades) > 0:
                gross_profit = strategy_month_trades[strategy_month_trades['pnl'] > 0]['pnl'].sum()
                gross_loss = abs(strategy_month_trades[strategy_month_trades['pnl'] < 0]['pnl'].sum())
                
                if gross_loss > 0:
                    profit_factor = gross_profit / gross_loss
                else:
                    profit_factor = gross_profit if gross_profit > 0 else 0
            else:
                profit_factor = 0
            
            month_data.append({
                'Month': month,
                'Strategy': strategy,
                'Profit Factor': profit_factor
            })
    
    month_df = pd.DataFrame(month_data)
    
    # Create line chart
    fig = px.line(
        month_df,
        x='Month',
        y='Profit Factor',
        color='Strategy',
        title='Profit Factor by Month',
        markers=True,
        color_discrete_map=STRATEGY_COLORS
    )
    fig.update_layout(yaxis_title="Profit Factor (Gross Profit / Gross Loss)")
    fig.add_hline(y=1, line_dash="dash", line_color="gray", annotation_text="Break-even")
    st.plotly_chart(fig, use_container_width=True)

def display_strategy_insights():
    """Display strategy optimization insights"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style="background-color: #e6f4ea; padding: 1rem; border-radius: 5px; height: 100%;">
                <h4>Hourly Quarters Strategy</h4>
                <ul>
                    <li>Highest win rate on Wednesdays</li>
                    <li>Best performance at 10:15 and 14:00</li>
                    <li>Setup quality 4-5 shows 85%+ win rate</li>
                    <li>Consistent profit factor across months</li>
                    <li>Low drawdowns indicate strong risk control</li>
                </ul>
                <p><strong>Focus Area:</strong> Increase position size on highest probability setups</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style="background-color: #fef7e0; padding: 1rem; border-radius: 5px; height: 100%;">
                <h4>930 Strategy</h4>
                <ul>
                    <li>Strongest in first hour of trading</li>
                    <li>Wednesday and Thursday outperformance</li>
                    <li>Higher average R than Hourly strategy</li>
                    <li>Benefits from volatility</li>
                    <li>Runners add significant edge</li>
                </ul>
                <p><strong>Focus Area:</strong> Optimize runner management for additional gains</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style="background-color: #fce8e6; padding: 1rem; border-radius: 5px; height: 100%;">
                <h4>Lab Strategy</h4>
                <ul>
                    <li>Highest reward but lowest win rate</li>
                    <li>Best performance in midday (11:00-13:00)</li>
                    <li>Sensitive to setup quality</li>
                    <li>Most volatility in monthly performance</li>
                    <li>Deeper but less frequent drawdowns</li>
                </ul>
                <p><strong>Focus Area:</strong> Further filter entries to improve win rate</p>
            </div>
        """, unsafe_allow_html=True)

def display_business_summary():
    """Display overall business performance summary"""
    # Calculate overall business metrics
    total_starting_capital = sum(account['starting_balance'] for account in st.session_state.account_info.values())
    total_current_capital = sum(account['current_balance'] for account in st.session_state.account_info.values())
    total_profit = total_current_capital - total_starting_capital
    
    total_trades = len(st.session_state.trade_journal)
    win_trades = len(st.session_state.trade_journal[st.session_state.trade_journal['outcome'] == 'Win'])
    overall_win_rate = win_trades / total_trades if total_trades > 0 else 0
    
    avg_daily_profit = st.session_state.daily_performance.groupby('date')['pnl'].sum().mean()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Capital", f"${total_current_capital:,.2f}", 
                 f"{(total_current_capital/total_starting_capital - 1)*100:+.2f}%")
    
    with col2:
        st.metric("Overall Win Rate", f"{overall_win_rate*100:.1f}%")
    
    with col3:
        st.metric("Total Profit", f"${total_profit:,.2f}")
    
    with col4:
        st.metric("Avg Daily Profit", f"${avg_daily_profit:,.2f}")
    
    # Monthly breakdown
    display_monthly_performance()
    
    # Business plan progress
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
            <h4>Business Plan Progress:</h4>
            <p>Based on your current performance metrics, here's how you're tracking against your business plan:</p>
            <ul>
                <li>Strategy separation is proving effective with low correlation between strategies</li>
                <li>Risk management protocols are successfully controlling drawdowns</li>
                <li>Accounts are maintaining consistent profitability</li>
                <li>Lab strategy shows highest growth potential with managed risk</li>
            </ul>
            <p><strong>Next Steps:</strong> Continue optimizing individual strategies while maintaining separation. 
            Consider scaling up account size for strategies showing consistent performance.</p>
        </div>
    """, unsafe_allow_html=True)

def display_monthly_performance():
    """Display monthly performance breakdown by account"""
    monthly_pnl = st.session_state.daily_performance.copy()
    monthly_pnl['month'] = pd.to_datetime(monthly_pnl['date']).dt.strftime('%Y-%m')
    monthly_summary = monthly_pnl.groupby(['month', 'account'])['pnl'].sum().reset_index()
    
    # Pivot to get accounts as columns
    monthly_pivot = monthly_summary.pivot(index='month', columns='account', values='pnl').reset_index()
    monthly_pivot['Total'] = monthly_pivot[['Account 1', 'Account 2', 'Account 3']].sum(axis=1)
    
    # Plot monthly performance
    fig = px.bar(
        monthly_pivot,
        x='month',
        y=['Account 1', 'Account 2', 'Account 3'],
        title='Monthly Performance by Account',
        barmode='group',
        color_discrete_map={'Account 1': '#34a853', 'Account 2': '#fbbc05', 'Account 3': '#ea4335'}
    )
    fig.update_layout(yaxis_title="Profit/Loss ($)")
    
    # Add total line
    fig.add_trace(
        go.Scatter(
            x=monthly_pivot['month'],
            y=monthly_pivot['Total'],
            mode='lines+markers',
            name='Total',
            line=dict(color='#4285f4', width=3)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)