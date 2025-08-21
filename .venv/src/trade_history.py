from .db import supabase_conn   
from .accounts import MT5_Class
import requests 
import os
import json as js
import datetime
from dotenv import load_dotenv
load_dotenv()
class Trader_History:
    
    def __init__(self):
    
        self.supabase = supabase_conn()
        self.acc = MT5_Class()
    
    async def get_all_trade_history(self):
        try:
            trade_hist= self.supabase.table("trade_history").select("*").execute()
            
            return trade_hist.data
            
        except Exception as e:
            return e
        
    async def get_trade_history_by_acc(self, acc_id:int):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).execute()
            
            return trade_hist.data
        except Exception as e:
            return e
    async def get_mt5_trade_history_by_acc(self, acc_id:int,pos_id:int):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).eq("position_id",pos_id).execute()
            
            return trade_hist.data
        except Exception as e:
            return e
        
    async def get_mt5_trade_history_by_position_id(self, pos_id:int,server:str):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("position_id",pos_id).execute()
            
            return trade_hist.data
        except Exception as e:
            return e
        
    async def insert_trade(self, data):
        try:
            trade_hist = self.supabase.table("trade_history").insert(data).execute()
        
            return trade_hist.data
        except Exception as e:
            return e
        
    async def get_user_last_trade(self,acc_id):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).order('exit_time', desc=True).limit(1).execute()
            return trade_hist.data
        except Exception as e:
            return e
        
    # async def get_all_mt5_user_last_trade(self):
    #     try:
    #         trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).order('exit_time', desc=True).limit(1).execute()
    #         return trade_hist
    #     except Exception as e:
    #         return e 
    
    # async def get_all_user_last_trade(self):
    #     mt5_accounts = await self.acc.get_all_mt5_account()
    #     for acc in mt5_accounts:
    #         acc_det = await self.get_user_last_trade(acc_id=acc["id"])
           
    #         trade_time = datetime.datetime.strptime(acc_det[0]['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
    #         now = datetime.datetime.now(datetime.timezone.utc)
            
    #         if trade_time < now:
    #             # check if any trades have been made and completed between then and now
    #             print(acc_det[0])
    #             url = os.environ.get("MT5_SERVER_HOST")+"/deal"
    #             headers = {
    #                 "Content-Type": "application/json"  
    #             }
    #             body = {
    #                 "login":acc["account_no"],
    #                 "password": acc["password"],
    #                 "server":acc["server_name"],
    #                 "platform": acc["platform"],
    #                 "from_": trade_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                    
    #             }
    #             # Gett the users mt5 trade history
    #             trade_data = requests.post(url=url, data=js.dumps(body),timeout=10, headers=headers)
                
    #             user_data_json = trade_data.json()
    #             print(user_data_json)
    #             pass
            
            
    #     pass