from .models import Acc_Model
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
                            "password": acc.password,
                            "platform":acc.platform,
                            "server_name":acc_info["server"],
                            "updated_at": datetime.datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")    
                        }
                        ).execute()
                    
                    # Check if that account has information stored in the trade history table to see if the account has been setup before
                    
                    # Check if the storing data and the getting the account history were successfull
                    if user_acc and user_data_json:
                        
                        # Insert the user data in the database
                        # Loop through the account data to map into a datatype to be able to insert bulk data
                        for key in user_data_json: 
                            
                            # Check if the trade has been executed
                            if user_data_json[key]["order"]["entry"] != None and user_data_json[key]["order"]["exit"] != None and user_data_json[key]["deal"]["entry"] != None and user_data_json[key]["deal"]["exit"] != None:
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
                                    "sl_price": float(user_data_json[key]["order"]["exit"].get('sl')),
                                    "tp_price": float(user_data_json[key]["order"]["exit"].get('tp')),
                                    "swap": float(user_data_json[key]["deal"]["exit"]["swap"]),
                                    "account_id": user_acc.data[0]["id"],
                                    "trade_type": trade_type,
                                }
                                
                                # Append the trade_data to a list for the bulk create
                                trade_list.append(trade_data)
                        
                        # Insert the trade history into the database
                        trade_hist = self.supabase.table("trade_history").insert(trade_list).execute()  
                        
                        # Check if the data was inserted succesfully
                        
                            
                        return trade_hist           
                    
        except Exception as e:
            return e
        
        
    '''
    Get MT5 account details
    '''   
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
        
    '''
    Get account information by id
    '''     
    async def get_account_by_id(self,id:int):
        try:
            acc_details = self.supabase.table("accounts").select("*").eq("id",id).execute()
            
            return acc_details.data
        except Exception as e:
            return e

    '''
    Get account information by account number
    '''         
    async def get_mt5_account_by_acc_no(self,acc_no:int,server:str):
        try:
            acc_details = self.supabase.table("accounts").select("*").eq("account_no",acc_no).eq('platform','mt5').eq('server_name',server).execute()
            
            return acc_details.data
        except Exception as e:
            return e
    
    '''
    Get all account belonging to a particular user
    '''        
    async def get_all_user_account(self, user_id:str):
        try:
            accounts =   self.supabase.table("accounts").select("*").eq("user_id",user_id).execute()
            
            return accounts
        except Exception as e:
            return e
        
    # async def get_last_account_update():
    #     try:
    #         pass
    #     except Exception as e:
    #         return e
    
    '''
    Update user account information
    '''     
    async def update_account_info(self, id:int, data:dict):
        try:
            acc_info =  self.supabase.table("accounts").update(data).eq("id",id).execute()
            return acc_info
        except Exception as e:
            return e       
        
    async def get_all_mt5_account(self):
        try:
            acc_details = self.supabase.table("accounts").select("*").eq('platform','mt5').execute()
            
            return acc_details.data
        except Exception as e:
            return e