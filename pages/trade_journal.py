import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math
from config import INSTRUMENT_POINT_VALUES
from utils.formatting import download_csv
from utils.calculations import calculate_point_value

def show():
    """Display the trade journal page"""
    st.title("Trade Journal")
    
    # Add New Trade Form
    st.markdown('<div class="tab-header">Add New Trade</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trade_date = st.date_input("Date", datetime.now())
        trade_time = st.time_input("Time", datetime.now().time())
        trade_account = st.selectbox("Account", ["Account 1", "Account 2", "Account 3"])
        
        # Auto-select strategy based on account
        trade_strategy = st.session_state.account_info[trade_account]['strategy']
    
    with col2:
        trade_instrument = st.selectbox("Instrument", list(INSTRUMENT_POINT_VALUES.keys()))
        trade_direction = st.selectbox("Direction", ["Long", "Short"])
        trade_entry = st.number_input("Entry Price", min_value=0.0, format="%.2f")
        trade_exit = st.number_input("Exit Price", min_value=0.0, format="%.2f")
    
    with col3:
        trade_stop = st.number_input("Stop Loss", min_value=0.0, format="%.2f")
        trade_size = st.number_input("Position Size (Contracts)", min_value=1, step=1)
        trade_outcome = st.selectbox("Outcome", ["Win", "Loss", "Breakeven"])
        trade_quality = st.selectbox("Setup Quality", [1, 2, 3, 4, 5], index=3)  # Default to 4
    
    trade_notes = st.text_area("Trade Notes")
    
    # Calculate P&L and R-multiple
    point_value = calculate_point_value(trade_instrument)
    
    if trade_direction == "Long":
        trade_pnl = (trade_exit - trade_entry) * trade_size * point_value
        trade_r = (trade_exit - trade_entry) / (trade_entry - trade_stop) if trade_stop > 0 and trade_entry > trade_stop else 0
    else:  # Short
        trade_pnl = (trade_entry - trade_exit) * trade_size * point_value
        trade_r = (trade_entry - trade_exit) / (trade_stop - trade_entry) if trade_stop > 0 and trade_stop > trade_entry else 0
    
    # Only show calculated values if entry and exit are not 0
    if trade_entry > 0 and trade_exit > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Calculated P&L: ${trade_pnl:.2f}")
        with col2:
            st.info(f"Calculated R-multiple: {trade_r:.2f}")
    
    if st.button("Add Trade"):
        if trade_entry > 0 and trade_exit > 0 and trade_stop > 0:
            # Add the trade to the journal
            new_trade = {
                'date': trade_date.strftime('%Y-%m-%d'),
                'time': trade_time.strftime('%H:%M'),
                'account': trade_account,
                'strategy': trade_strategy,
                'instrument': trade_instrument,
                'direction': trade_direction,
                'entry_price': trade_entry,
                'exit_price': trade_exit,
                'stop_loss': trade_stop,
                'position_size': trade_size,
                'pnl': trade_pnl,
                'r_multiple': trade_r,
                'outcome': trade_outcome,
                'setup_quality': trade_quality,
                'execution_quality': 4,  # Default value
                'notes': trade_notes
            }
            
            # Add to the trade journal
            st.session_state.trade_journal = pd.concat([pd.DataFrame([new_trade]), st.session_state.trade_journal], 
                                                     ignore_index=True)
            
            # Update the daily performance
            today = trade_date.strftime('%Y-%m-%d')
            
            # Check if there's already an entry for this date and account
            mask = (st.session_state.daily_performance['date'] == today) & \
                  (st.session_state.daily_performance['account'] == trade_account)
            
            if mask.any():
                # Update existing entry
                st.session_state.daily_performance.loc[mask, 'pnl'] += trade_pnl
            else:
                # Add new entry
                new_day = {
                    'date': today,
                    'account': trade_account,
                    'pnl': trade_pnl
                }
                st.session_state.daily_performance = pd.concat([pd.DataFrame([new_day]), 
                                                              st.session_state.daily_performance], 
                                                             ignore_index=True)
            
            # Update account balance
            st.session_state.account_info[trade_account]['current_balance'] += trade_pnl
            
            st.success("Trade added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields (Entry, Exit, Stop Loss)")
    
    # Trade History
    st.markdown('<div class="tab-header">Trade History</div>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_account = st.multiselect("Filter by Account", 
                                      options=["Account 1", "Account 2", "Account 3"],
                                      default=["Account 1", "Account 2", "Account 3"])
    
    with col2:
        filter_outcome = st.multiselect("Filter by Outcome", 
                                      options=["Win", "Loss", "Breakeven"],
                                      default=["Win", "Loss", "Breakeven"])
    
    with col3:
        date_options = ["All Time", "This Week", "This Month", "Last 30 Days"]
        filter_date = st.selectbox("Filter by Date", options=date_options)
    
    # Apply filters
    filtered_trades = st.session_state.trade_journal.copy()
    
    if filter_account:
        filtered_trades = filtered_trades[filtered_trades['account'].isin(filter_account)]
    
    if filter_outcome:
        filtered_trades = filtered_trades[filtered_trades['outcome'].isin(filter_outcome)]
    
    if filter_date != "All Time":
        today = datetime.now().date()
        if filter_date == "This Week":
            start_date = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        elif filter_date == "This Month":
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
        elif filter_date == "Last 30 Days":
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        
        filtered_trades = filtered_trades[filtered_trades['date'] >= start_date]
    
    # Sort by date descending
    filtered_trades = filtered_trades.sort_values('date', ascending=False)
    
    # Show the dataframe with styling
    st.dataframe(
        filtered_trades[['date', 'time', 'account', 'strategy', 'instrument', 'direction', 
                      'entry_price', 'exit_price', 'pnl', 'r_multiple', 'outcome', 'notes']],
        use_container_width=True,
        hide_index=True
    )
    
    # Summary metrics for filtered trades
    if not filtered_trades.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_trades = len(filtered_trades)
            win_trades = len(filtered_trades[filtered_trades['outcome'] == 'Win'])
            win_rate = win_trades / total_trades if total_trades > 0 else 0
            st.metric("Win Rate", f"{win_rate*100:.1f}%")
        
        with col2:
            net_pnl = filtered_trades['pnl'].sum()
            st.metric("Net P&L", f"${net_pnl:.2f}")
        
        with col3:
            avg_r = filtered_trades['r_multiple'].mean()
            st.metric("Average R", f"{avg_r:.2f}")
        
        with col4:
            win_r = filtered_trades[filtered_trades['outcome'] == 'Win']['r_multiple'].mean()
            loss_r = filtered_trades[filtered_trades['outcome'] == 'Loss']['r_multiple'].mean()
            expectancy = (win_rate * win_r) + ((1 - win_rate) * loss_r)
            st.metric("Expectancy", f"{expectancy:.2f}")
    
    # Download option
    st.markdown(download_csv(filtered_trades, "trade_journal"), unsafe_allow_html=True)