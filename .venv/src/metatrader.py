from .model import Acc_Model
import requests
from dotenv import load_dotenv
load_dotenv()
import datetime
import os
from .db import supabase_conn
import asyncio
from fastapi.encoders import jsonable_encoder
import json as js

class MT5_Class:
    
    def __init__(self):
        
        self.supabase = supabase_conn()
      
    async def account_setup(self,user_id:str,acc:Acc_Model):
        try:
            
            # Store the user credential in the database 
            # user_acc = self.supabase.table("accounts").insert().execute()
            
            match acc.platform:
                
                case "mt5":
                    trade_list=[]
                    url = os.environ.get("MT5_SERVER_HOST")+"/setup"
                    headers = {
                        "Content-Type": "application/json"
                        
                    }
                    # Gett the users mt5 trade history
                    user_data = requests.post(url=url, data=js.dumps(jsonable_encoder(acc)),timeout=10, headers=headers)
                    
                    # Convert the data to json format
                    user_data_json = user_data.json()
                    
                    #Filter the completed deal, Store in the database
                    acc_info = await self.get_account_detail(acc)
                
                    # Store the account details in the database
                    user_acc = self.supabase.table("accounts").insert(
                        {
                            "user_id":user_id,
                            "broker_name":acc_info["company"],
                            "currency": acc_info["currency"],
                            "balance":acc_info["balance"],
                            "leverage":acc_info["leverage"],
                            "account_no":acc_info["login"],
                            "platform":acc.platform,
                            "server_name":acc_info["server"],
                            "updated_at": datetime.datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")    
                        }
                        ).execute()
                    
                    
                    # Check if the storing data and the getting the account history were successfull
                    if user_acc and user_data_json:
                        
                        # Insert the user data in the database
                        # Loop through the account data to map into a datatype to be able to insert bulk data
                        for key in user_data_json: 
                            
                            # Chek if the trade has been executed
                            if user_data_json[key]["order"]["entry"] != None and user_data_json[key]["order"]["exit"] != None and user_data_json[key]["deal"]["entry"] != None and user_data_json[key]["deal"]["exit"]:
                                trade_type = None
                                
                                # Confirm the trade type
                                if user_data_json[key]["deal"]["entry"]["type"] == 0:
                                    trade_type = "buy"
                                elif user_data_json[key]["deal"]["entry"]["type"] == 1:
                                    trade_type = "sell"
                                    
                                # Figure out how to get the stoploss and take profit
                                
                                #Map the relevant information
                                trade_data = {
                                    "position_id": int(key),
                                    "entry_price": float(user_data_json[key]["deal"]["entry"]["price"]),
                                    "exit_price": float(user_data_json[key]["deal"]["exit"]["price"]),
                                    "volume": float(user_data_json[key]["deal"]["entry"]["volume"]),
                                    "commission":float(user_data_json[key]["deal"]["exit"]["commission"]),
                                    "fee": float(user_data_json[key]["deal"]["exit"]["fee"]),
                                    "profit_loss": float(user_data_json[key]["deal"]["exit"]["profit"]),
                                    "symbol": str(user_data_json[key]["deal"]["exit"]["symbol"]),
                                    "entry_time": datetime.datetime.fromtimestamp(int(user_data_json[key]["deal"]["entry"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                    "exit_time": datetime.datetime.fromtimestamp(int(user_data_json[key]["deal"]["exit"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                    "sl_price": None,
                                    "tp_price": None,
                                    "swap": float(user_data_json[key]["deal"]["exit"]["swap"]),
                                    "account_id": user_acc.data[0]["id"],
                                    "trade_type": trade_type,
                                }
                                
                                # Append the trade_data to a list for the bulk create
                                trade_list.append(trade_data)
                        
                        # Insert the trade history into the database
                        trade_hist = self.supabase.table("trade_history").insert(trade_list).execute()  
                        
                        # Check if the data was inserted succesfully
                        if trade_hist:
                            
                            return trade_hist           
                    
        except Exception as e:
            return e
        
    async def get_account_detail(self,acc:Acc_Model):
        try:
            
            # Get the account details
            url = os.environ.get("MT5_SERVER_HOST")+"/account_info"
            headers = {
                "Content-Type": "application/json"  
            }
            user_data = requests.post(url=url, data=js.dumps(jsonable_encoder(acc)),timeout=10, headers=headers)
            
            return user_data.json()
        except Exception as e:
            return e