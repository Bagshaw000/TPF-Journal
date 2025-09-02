    # async def get_open_position(self,acc_id:str):
    #     try:
    #         # Check the last update date
            
    #         last_update = self.get_trade_account_by_id(acc_id)
            
            
    #         pass
    #     except Exception as e:
    #         return e   
from .db import supabase_conn   
from .account import Accounts
from .trade_history import Trader_History
import datetime
import requests 
import os
import json as js
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder

load_dotenv()
class Position:
        
    def __init__(self):
    
        self.supabase = supabase_conn()
        self.acc = Accounts()
        self.trade_hist = Trader_History()
    
    async def store_mt5_open_pos(self,open_pos:dict):
        try:
            # Create a list to store all the new position for a bulk create
            trade_list = []
            print(open_pos)
            for trade in open_pos:
                
                # Get the server name for the account
                server:str = open_pos[trade]['server']
                
                # Get the mt5 account with the account number, server and mt5 platform exist
                acc_det = await self.acc.get_mt5_account_by_acc_no(int(trade), server)
                
                
                # Loop through all open position on this account
                for pos in open_pos[trade]['position']:
                    
                    # Assign none to trader type to be later used to be assigned to either buy or sell
                    trade_type = None
                    
                    # Check if the trade has been added to the trade history which mean it is a complete trade
                    trade_hist = await self.trade_hist.get_mt5_trade_history_by_acc(int(acc_det[0]['id']), int(pos))
                    
                    # Check in the open trade if a trade with same position attache to the same account and server exist if so it is an ongoing trade
                    open_trade = await self.get_mt5_open_trade_pos_id_acc_id(int(acc_det[0]['id']), int(pos), str(server))
                    
                    # Determin trade type buy or sell
                    match int(open_pos[trade]['position'][pos]['type']):
                        case 0:
                            trade_type = "buy"
                        case 1:
                            trade_type = "sell"
                    
                    # Assign the position object parameters
                    pos_data = {
                            "position_id" :  (open_pos[trade]['position'][pos]['ticket']) ,
                            "entry_price":(open_pos[trade]['position'][pos]['price_open']),
                            "current_price":(open_pos[trade]['position'][pos]['price_current']),
                            "volume":(open_pos[trade]['position'][pos]['volume']),
                            "commission":(open_pos[trade]['position'][pos].get('commission')),
                            "fee":(open_pos[trade]['position'][pos].get('fee')),
                            "profit_loss":(open_pos[trade]['position'][pos]['profit']),
                            "symbol":(open_pos[trade]['position'][pos]['symbol']),
                            "sl_price":(open_pos[trade]['position'][pos].get('sl')),
                            "tp_price":(open_pos[trade]['position'][pos].get('tp')),
                            "swap":(open_pos[trade]['position'][pos]['swap']),
                            "trade_type":(trade_type), 
                            "account_id":(acc_det[0]['id']),
                            "platform":("mt5"),
                            "server_name":(server),
                            "updated_at":datetime.datetime.fromtimestamp(int(open_pos[trade]['position'][pos]['time_update_msc'])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            "entry_time":datetime.datetime.fromtimestamp(int(open_pos[trade]['position'][pos]['time_msc'])/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                        }
                  
                    # If trade not completed then a new trade
                    if not trade_hist and not open_trade:
                        # Append new position to a tradelist for bulk create  
                        trade_list.append(pos_data)  

                    elif open_trade:
                        # Old position check if it is a completed position api call

                        # Get the position data from the mt5 server 
                        url = os.environ.get("MT5_SERVER_HOST")+"/deal/pos_id"
                        headers = {
                            "Content-Type": "application/json"  
                        }
                        body = {
                            "pos_id":pos
                        }
                        # Gett the users mt5 trade history
                        trade_data = requests.post(url=url, data=js.dumps(body),timeout=10, headers=headers)
                        
                        user_data_json = trade_data.json()
                        
                        # Check if the order and deal has exit data if not ongoin trade
                        if user_data_json["order"]["exit"] == None and user_data_json["deal"]["exit"]== None:
                            # Update ongoing trade data
                            await self.update_open_pos(pos_data,open_trade[0]['id'])
                        else:
                            # Completed trade
                           
                            trade_data = {
                                    "position_id": (open_pos[trade]['position'][pos]['ticket']),
                                    "entry_price": (user_data_json["deal"]["entry"]["price"]),
                                    "exit_price": (user_data_json["deal"]["exit"]["price"]),
                                    "volume": (user_data_json["deal"]["entry"]["volume"]),
                                    "commission":(user_data_json["deal"]["exit"]["commission"]),
                                    "fee": (user_data_json["deal"]["exit"]["fee"]),
                                    "profit_loss": (user_data_json["deal"]["exit"]["profit"]),
                                    "symbol": (user_data_json["deal"]["exit"]["symbol"]),
                                    "entry_time": datetime.datetime.fromtimestamp(int(user_data_json["deal"]["entry"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                    "exit_time": datetime.datetime.fromtimestamp(int(user_data_json["deal"]["exit"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                    "sl_price": (open_pos[trade]['position'][pos].get('sl')),
                                    "tp_price": (open_pos[trade]['position'][pos].get('tp')),
                                    "swap": (user_data_json["deal"]["exit"]["swap"]),
                                    "account_id": acc_det[0]['id'],
                                    "trade_type": trade_type,

                            }
                             # Delete data from open trade and add into trade history
                            await self.delete_open_pos(open_trade[0]['id'])
                            #Add to trade history
                            await  self.trade_hist.insert_trade(trade_data)
                            
                            

            # Check if any new trade were added to the trade list if so bulk add new position
            if len(trade_list)!= 0 :              
               await self.supabase.table("open_trade").insert(trade_list).execute()
                           
        except Exception as e :
            return e
        
    async def get_mt5_open_trade_acc(self, acc_id:int,server:str):
        try:
            open_pos = self.supabase.table("open_trade").select('*').eq('account_id', acc_id).eq("platform","mt5").eq('server_name',server).execute()
            print(open_pos)
            return open_pos.data
        except  Exception as e:
            return e 
        
    async def get_mt5_open_trade_pos_id_acc_id(self, acc_id:int,pos_id:int,server:str):
        try:
            open_pos = self.supabase.table("open_trade").select('*').eq('account_id', acc_id).eq('position_id', pos_id).eq("platform","mt5").eq('server_name',server).execute()
            
            return open_pos.data
        except  Exception as e:
            return e
        
    async def get_mt5_open_trade_acc_id(self, acc_id:int,server:str):
        try:
            open_pos = self.supabase.table("open_trade").select('*').eq('account_id', acc_id).eq("platform","mt5").eq('server_name',server).execute()
            
            return open_pos.data
        except  Exception as e:
            return e
        
    async def update_open_pos(self, data,id:int):
        try:
            open_pos = self.supabase.table("open_trade").update(data).eq("id", id).execute()
            return open_pos.data
        except Exception as e:
            return e 
    
    async def delete_open_pos(self, id:int):
        try:
            open_pos = self.supabase.table("open_trade").delete().eq("id", id).execute()
            return open_pos.data
        except Exception as e:
            return e 
     