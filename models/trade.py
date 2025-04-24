from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Trade:
    """Data model for a single trade"""
    date: str
    time: str
    account: str
    strategy: str
    instrument: str
    direction: str
    entry_price: float
    exit_price: float
    stop_loss: float
    position_size: int
    pnl: float
    r_multiple: float
    outcome: str
    setup_quality: int
    execution_quality: Optional[int] = None
    notes: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data):
        """Create a Trade object from a dictionary"""
        return cls(
            date=data['date'],
            time=data['time'],
            account=data['account'],
            strategy=data['strategy'],
            instrument=data['instrument'],
            direction=data['direction'],
            entry_price=float(data['entry_price']),
            exit_price=float(data['exit_price']),
            stop_loss=float(data['stop_loss']),
            position_size=int(data['position_size']),
            pnl=float(data['pnl']),
            r_multiple=float(data['r_multiple']),
            outcome=data['outcome'],
            setup_quality=int(data['setup_quality']),
            execution_quality=int(data['execution_quality']) if 'execution_quality' in data else None,
            notes=data['notes'] if 'notes' in data else None
        )
    
    def to_dict(self):
        """Convert Trade object to a dictionary"""
        return {
            'date': self.date,
            'time': self.time,
            'account': self.account,
            'strategy': self.strategy,
            'instrument': self.instrument,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'stop_loss': self.stop_loss,
            'position_size': self.position_size,
            'pnl': self.pnl,
            'r_multiple': self.r_multiple,
            'outcome': self.outcome,
            'setup_quality': self.setup_quality,
            'execution_quality': self.execution_quality,
            'notes': self.notes
        }

@dataclass
class DailyPerformance:
    """Data model for daily performance"""
    date: str
    account: str
    pnl: float
    
    @classmethod
    def from_dict(cls, data):
        """Create a DailyPerformance object from a dictionary"""
        return cls(
            date=data['date'],
            account=data['account'],
            pnl=float(data['pnl'])
        )
    
    def to_dict(self):
        """Convert DailyPerformance object to a dictionary"""
        return {
            'date': self.date,
            'account': self.account,
            'pnl': self.pnl
        }

@dataclass
class Account:
    """Data model for an account"""
    name: str
    strategy: str
    starting_balance: float
    current_balance: float
    risk_per_trade: float
    daily_stop: float
    weekly_stop: float
    start_date: str
    color: str = ""
    header_class: str = ""
    
    @classmethod
    def from_dict(cls, name, data):
        """Create an Account object from a dictionary"""
        return cls(
            name=name,
            strategy=data['strategy'],
            starting_balance=float(data['starting_balance']),
            current_balance=float(data['current_balance']),
            risk_per_trade=float(data['risk_per_trade']),
            daily_stop=float(data['daily_stop']),
            weekly_stop=float(data['weekly_stop']),
            start_date=data['start_date'],
            color=data.get('color', ""),
            header_class=data.get('header_class', "")
        )
    
    def to_dict(self):
        """Convert Account object to a dictionary"""
        return {
            'strategy': self.strategy,
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'risk_per_trade': self.risk_per_trade,
            'daily_stop': self.daily_stop,
            'weekly_stop': self.weekly_stop,
            'start_date': self.start_date,
            'color': self.color,
            'header_class': self.header_class
        }