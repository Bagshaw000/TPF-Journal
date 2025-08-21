from .db import supabase_conn
import requests 
import os
import json as js
import datetime
from .mt5 import Mt5_Action 
from .model import Mt5_Model
class Accounts:
    
    def __init__(self):
        self.supabase = supabase_conn()
        self.mt5= Mt5_Action()
        
    '''
    Get all account belonging to a particular user
    '''        
    async def get_all_mt5_account(self):
        try:
            accounts =   self.supabase.table("accounts").select("*").eq("platform","mt5").execute()
           
            return accounts.data
        except Exception as e:
            return e
        
    async def get_all_user_last_trade(self, acc):
        
        # Create an empty list that will be used to add all trades to update user account
        trade_list = []
        
        # Assign the trade type to None this will be reassigned later on 
        trade_type = None
        
        # Get the last trade for this particular account
        acc_det = await self.get_user_last_trade(acc_id=acc["id"])
        
        # Check any information is return 
        if not acc_det:
          return
        
        # Get the time of the last trade
        trade_time = datetime.datetime.strptime(acc_det[0]['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Check if the trade time is less than current time
        if trade_time < now:
            
            # Get the user login data
            login_data: Mt5_Model = Mt5_Model(login=acc["account_no"],password=acc["password"], server=acc["server_name"],platform=acc["platform"])

            # Check if any trade occurred within that period
            trade_hist_data = await self.mt5.get_deal_history(trade_time.replace(tzinfo=None),now.replace(tzinfo=None), login_data)
           
            # Check if there is a trade returned
            if not trade_hist_data :
        
                return 
            
            # If trades exist then loop through
            for key in trade_hist_data:
                
                # Check if it a completed trade
                if trade_hist_data[key]["order"]["exit"] != None and trade_hist_data[key]["deal"]["exit"] != None:
                    continue
                
                # Check if the trade posision id attached to these account details  are in the database to avoid duplicate 
                pos_in_db = await self.get_mt5_trade_history_by_acc(acc["id"],key)
                
                # If it is in data base then dont add
                if pos_in_db:
                    continue
                
                # Check if the trade type is buy or sell
                if trade_hist_data[key]["deal"]["entry"]["type"] == 0:
                    trade_type = "buy"
                elif trade_hist_data[key]["deal"]["entry"]["type"] == 1:
                    trade_type = "sell"

                # Model the trade to how the database table
                trade_data = {
                                "position_id": int(key),
                                "entry_price": float(trade_hist_data[key]["deal"]["entry"]["price"]),
                                "exit_price": float(trade_hist_data[key]["deal"]["exit"]["price"]),
                                "volume": float(trade_hist_data[key]["deal"]["entry"]["volume"]),
                                "commission":float(trade_hist_data[key]["deal"]["exit"]["commission"]),
                                "fee": float(trade_hist_data[key]["deal"]["exit"]["fee"]),
                                "profit_loss": float(trade_hist_data[key]["deal"]["exit"]["profit"]),
                                "symbol": str(trade_hist_data[key]["deal"]["exit"]["symbol"]),
                                "entry_time": datetime.datetime.fromtimestamp(int(trade_hist_data[key]["deal"]["entry"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                "exit_time": datetime.datetime.fromtimestamp(int(trade_hist_data[key]["deal"]["exit"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                "sl_price": float(trade_hist_data[key]["order"]["exit"].get('sl')),
                                "tp_price": float(trade_hist_data[key]["order"]["exit"].get('tp')),
                                "swap": float(trade_hist_data[key]["deal"]["exit"]["swap"]),
                                "account_id": acc["id"],
                                "trade_type": trade_type,
                            }
                
                # Append trade to trade list
                trade_list.append(trade_data)
                    
            
            # Insert all trade history into the database
            if trade_list:
                self.supabase.table("trade_history").insert(trade_list).execute()      
             

    '''
    This function gets the user last trade
    '''
    async def get_user_last_trade(self,acc_id):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).order('exit_time', desc=True).limit(1).execute()
            return trade_hist.data
        except Exception as e:
            return e
    
    '''
    This function checks if position id already associated with this account
    '''
    async def get_mt5_trade_history_by_acc(self, acc_id:int,pos_id:int):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).eq("position_id",pos_id).execute()
            
            return trade_hist.data
        except Exception as e:
            return e
        