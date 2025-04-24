# App settings
APP_TITLE = "Prop Firm Trading Tracker"
APP_ICON = "📈"
DEFAULT_PAGE = 0

# Data storage settings
DATA_DIR = "data_storage"

# Account settings
ACCOUNT_CONFIGS = {
    'Account 1': {
        'name': 'Account 1', 
        'strategy': 'Hourly Quarters', 
        'starting_balance': 150000,
        'risk_per_trade': 0.01, 
        'daily_stop': 0.02, 
        'weekly_stop': 0.05, 
        'color': '#34a853',
        'header_class': 'account1-header'
    },
    'Account 2': {
        'name': 'Account 2', 
        'strategy': '930 Strategy', 
        'starting_balance': 150000,
        'risk_per_trade': 0.01, 
        'daily_stop': 0.02, 
        'weekly_stop': 0.05,
        'color': '#fbbc05',
        'header_class': 'account2-header'
    },
    'Account 3': {
        'name': 'Account 3', 
        'strategy': 'Lab Strategy', 
        'starting_balance': 100000,
        'risk_per_trade': 0.0075, 
        'daily_stop': 0.025, 
        'weekly_stop': 0.06,
        'color': '#ea4335',
        'header_class': 'account3-header'
    }
}

# Chart colors
STRATEGY_COLORS = {
    'Hourly Quarters': '#34a853',
    '930 Strategy': '#fbbc05',
    'Lab Strategy': '#ea4335'
}

# Point values for different instruments
INSTRUMENT_POINT_VALUES = {
    'MES': 5.0,
    'MNQ': 2.0,
    'ES': 50.0,
    'NQ': 20.0,
    'YM': 5.0,
    'RTY': 5.0,
    'CL': 1000.0,
    'GC': 100.0
}