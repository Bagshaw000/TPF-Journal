from datetime import datetime
from pydantic import BaseModel,Field
class Mt5_Model(BaseModel):
    login:int
    password:str
    server: str
    timeout:str | None = None
    

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

class MT5Deal(BaseModel):
    
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
    
class MT5Order(BaseModel):
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
