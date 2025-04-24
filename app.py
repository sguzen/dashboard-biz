import streamlit as st
import os
from config import (
    APP_TITLE, 
    APP_ICON,
    DEFAULT_PAGE
)
from data.data_loader import load_data, save_data
from pages import dashboard, accounts, trade_journal, risk_calculator, analytics

# Set page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initial data loading
def initialize_data():
    if 'initialized' not in st.session_state:
        # Load data from files if they exist, otherwise use sample data
        st.session_state.trade_journal = load_data('trades')
        st.session_state.account_info = load_data('accounts') 
        st.session_state.daily_performance = load_data('performance')
        st.session_state.initialized = True

# Custom CSS
def load_css():
    with open(os.path.join("utils", "styles.css"), "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Navigation
def create_navigation():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", 
        ["Dashboard", "Account 1 (Hourly)", "Account 2 (930)", "Account 3 (Lab)", 
         "Trade Journal", "Risk Calculator", "Performance Analytics"],
        index=DEFAULT_PAGE)
    return page

# Main function
def main():
    initialize_data()
    load_css()
    page = create_navigation()
    
    # Route to the correct page
    if page == "Dashboard":
        dashboard.show()
    elif page == "Account 1 (Hourly)" or page == "Account 2 (930)" or page == "Account 3 (Lab)":
        account_name = page.split(" ")[0] + " " + page.split(" ")[1]
        accounts.show(account_name)
    elif page == "Trade Journal":
        trade_journal.show()
    elif page == "Risk Calculator":
        risk_calculator.show()
    elif page == "Performance Analytics":
        analytics.show()
    
    # Auto-save data on page change
    save_data('trades', st.session_state.trade_journal)
    save_data('accounts', st.session_state.account_info)
    save_data('performance', st.session_state.daily_performance)

if __name__ == "__main__":
    main()