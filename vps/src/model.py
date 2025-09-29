from datetime import datetime
from pydantic import BaseModel,Field
from enum import Enum

class Performance_Enum(str, Enum):
    yesterday = "y"
    this_week= "t-w"
    last_week= "l-w"
    this_month= "t-m"
    last_month = "l-m"
    last_three_month = "3-m"
    last_six_month= "6-m"
    last_twelve_month= "12-m"
    all_history = "*"
    
class Acc_Model(BaseModel):
    login:int
    password:str
    server: str
    timeout:str | None = None
    platform: str|None

class Deal_Req(Acc_Model):
    from_:datetime
    
class Pos_Id(BaseModel):
    pos_id: int

class Account_Info(BaseModel):
    
    login:int
    leverage:int
    balance:float
    profit: float
    equity: float
    margin_free: float
    name: str
    currency: str
    company:str

class MT5_Deal(BaseModel):
    
    ticket: int                                           # Unique deal ticket
    order: int                                            # Order that caused this deal
    time: datetime                                        # Execution time (converted from timestamp)
    time_msc: int                                         # Millisecond timestamp
    type: int                                             # Deal type (0=buy, 1=sell, etc.)
    entry: int                                            # Entry type (0=in, 1=out, 2=in/out)
    magic: int                                            # EA identifier
    position_id: int                                      # Related position
    reason: int                                           # Reason for the deal (e.g., stop loss)
    volume: float                                         # Volume traded
    price: float                                          # Price executed
    commission: float                                     # Commission paid
    swap: float                                           # Swap charged
    profit: float                                         # Profit or loss
    fee: float                                            # Additional broker fee
    symbol: str                                           # Traded symbol
    comment: str                                          # Broker or EA comment
    external_id: str                                      # Broker-side deal ID
    
class MT5_Order(BaseModel):
    ticket: int                                           # Unique order ticket
    time_setup: datetime                                  # Order setup time
    time_setup_msc: int                                   # Setup time in milliseconds
    time_done: datetime                                   # Execution completion time
    time_done_msc: int                                    # Execution done in milliseconds
    time_expiration: int                                  # Expiration time (if applicable)
    type: int                                             # Order type (e.g., 0=buy, 1=sell)
    type_time: int                                        # Order time type (e.g., 0=GTC)
    type_filling: int                                     # Filling type (e.g., 1=IOC)
    state: int                                            # Order state
    magic: int                                            # EA identifier
    position_id: int                                      # Associated position
    position_by_id: int                                   # Related position-by ID
    reason: int                                           # Order reason
    volume_initial: float                                 # Initial volume requested
    volume_current: float                                 # Remaining volume
    price_open: float                                     # Opening price
    sl: float                                             # Stop Loss
    tp: float                                             # Take Profit
    price_current: float                                  # Current price
    price_stoplimit: float                                # Stop Limit price
    symbol: str                                           # Traded symbol
    comment: str                                          # Order comment
    external_id: str                                      # Broker-defined order ID 



class Acc_Id(BaseModel):
    acc_id:int
    
class User(BaseModel):
    first_name:str |None = None
    last_name:str |None = None
    country: str |None = None
    last_update:str | None = None
    plan: str | None = None
    email: str 
    password: str 


class Account_Model(BaseModel):
    broker_name:str | None = None
    currency:str | None = None
    balance:int| None = None
    account_type:str | None = None
    account_no:int | None = None
    server_name:str | None = None
    platform:str | None = None
    max_risk:int | None = None
    initial_capital:float | None = None
    gross_profit:float | None = None
    gross_loss:float | None = None
    net_profit_loss:float | None = None
    percentage_profit_loss:str | None = None
    leverage:float | None = None
    user_id:str | None = None
    updated_at:datetime| None = None
    password:str | None = None


    
class Session(BaseModel):
    access_token:str
    refresh_token:str
    expires_in:int
    expires_at: int
    token_type:str
    
    
class Return_Type(BaseModel):
    status: bool
    msg: str | None
    data: object | str | None
    
class Auth_Id(BaseModel):
    id: str 

class Acc_Id(BaseModel):
    acc_id:int
    
class Performance_time(BaseModel):
    timeframe: Performance_Enum