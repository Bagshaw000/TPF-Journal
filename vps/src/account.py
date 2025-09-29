from collections import defaultdict
from .db import supabase_conn
import requests 
import os
import json as js
import datetime
from .mt5 import Mt5_Class
from .model import Acc_Model, Deal_Req,MT5_Deal,Return_Type
import MetaTrader5 as mt5
class Accounts:
    
    def __init__(self):
        self.supabase = supabase_conn()
        self.mt5= Mt5_Class()
        
        
    '''
    Get all account belonging to a particular user
    '''        
    async def get_all_mt5_account(self):
        try:
            accounts =  self.supabase.table("accounts").select("*").eq("platform","mt5").execute()
            
            return accounts.data
        except Exception as e:
            return e
    
    '''
    Get all trading accounts in the  
    '''
    async def get_all_account(self):
        try:
            
            accounts = self.supabase.table("accounts").select("*").execute()
            if accounts.data:
                return Return_Type(status=True, msg="Success", data=accounts.data)
            
            return  Return_Type(status=False, msg="Success", data=None)
        except Exception as e:
            return e
    
    '''
    Get all user accounts
    '''
    async def get_all_user_account(self, user_id:str):
        try:
            accounts = self.supabase.table("accounts").select("*").eq("user_id", user_id).execute()
            
            if accounts.data:
                return Return_Type(status=True, msg="Success", data=accounts.data)
            
            return  Return_Type(status=False, msg="Success", data=None)
        except Exception as e:
            return e
    
    '''
    ''' 
    async def get_acc_by_id(self, id:int):
        try:
            account = self.supabase.table("accounts").select("*").eq("id", id).execute()
            if account.data:
                return Return_Type(status=True, msg="success", data=account.data)  
            
            return Return_Type(status=False, msg="success", data=None)
        except Exception as e:
            return e
        
        
    async def update_acc_by_id(self, id:int, data:dict):
        try:
            account = self.supabase.table("accounts").update(data).eq("id",id).execute()
            
            if account.data:
                return Return_Type(status=True, msg="success", data=account.data)
            
            return Return_Type(status=False, msg="success", data=None)
        except Exception as e:
            return e
    
    '''
    This function checks if position id already associated with this account
    '''
    
        
    async def check_account_exist(self, acc_no:int,platform:str, server:str):
        try:
            account = self.supabase.table("accounts").select('*').eq("account_no",acc_no).eq("server_name",server).eq("platform",platform).execute()
            
            return account.data
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
        This Function is to setup a user account by API call
    '''
        
    async def account_setup(self,user_id:str,acc:Deal_Req,starting_bal:float)-> Return_Type:
        try:
            
            # Store the user credential in the database 
            # user_acc = self.supabase.table("accounts").insert().execute()
            # Check user id aswell
            user_acc = await self.check_account_exist(acc.login,acc.platform,acc.server)
            
            if len(user_acc) == 0:
            
                match acc.platform:
                    
                    case "mt5":
                    
                        # #Filter the completed deal, Store in the database
                        acc_info = await self.mt5.get_account_details(acc)
                        
                        user_data = await self.mt5.setup_Account(acc)
                    
                        # Store the account details in the database
                        
                        # Check if this account has been stored befoer
                        
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
                                "updated_at": datetime.datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")  ,
                                "initial_capital" : starting_bal 
                            }
                            ).execute()
                        
                        # Check if that account has information stored in the trade history table to see if the account has been setup before
                        
                        # Check if the storing data and the getting the account history were successfull
                        if user_acc and user_data:
                            
                            # Map the trade details to be stored into the database
                            trade_list = await self.store_mt5_trade_histroy(user_data,user_acc.data[0]["id"] )

                            
                            # Map the Funding details
                            fund_data = await self.mt5.get_funding_details(acc,user_acc.data[0]["id"])
                            store_fund_detials = await self.store_funding_details(fund_data, user_acc.data[0]["id"])
                         
                            # Insert the trade history into the database 
                        
                            if store_fund_detials.status == False:
                                return store_fund_detials
                            
                            if trade_list.status == False:
                                return trade_list
            
              
                        
        
                        # Check if the data was inserted succesfully
                        
                        return Return_Type(status=True, msg="Success", data=None)
            return Return_Type(status=True, msg="Account already exist", data=None)
                                    
                
        except Exception as e:
            return e

    async def store_mt5_trade_histroy(self, user_data:dict, acc_id:int):
        
        try:
            
            # Insert the user data in the database
            # Loop through the account data to map into a datatype to be able to insert bulk data
            trade_list=[]
            
            for key in user_data: 
                        
                # Check if the trade has been executed
                if user_data[key]["order"]["entry"] != None and user_data[key]["order"]["exit"] != None and user_data[key]["deal"]["entry"] != None and user_data[key]["deal"]["exit"] != None:
                    trade_type = None
                    
                    # Confirm the trade type
                    if user_data[key]["deal"]["entry"]["type"] == 0:
                        trade_type = "buy"
                    elif user_data[key]["deal"]["entry"]["type"] == 1:
                        trade_type = "sell"
                        
                    # Figure out how to get the stoploss and take profit
                    
                    #Map the relevant information
                    trade_data = {
                        "position_id": int(key),
                        "entry_price": float(user_data[key]["deal"]["entry"]["price"]),
                        "exit_price": float(user_data[key]["deal"]["exit"]["price"]),
                        "volume": float(user_data[key]["deal"]["entry"]["volume"]),
                        "commission":float(user_data[key]["deal"]["exit"]["commission"]),
                        "fee": float(user_data[key]["deal"]["exit"]["fee"]),
                        "profit_loss": float(user_data[key]["deal"]["exit"]["profit"]),
                        "symbol": str(user_data[key]["deal"]["exit"]["symbol"]),
                        "entry_time": datetime.datetime.fromtimestamp(int(user_data[key]["deal"]["entry"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "exit_time": datetime.datetime.fromtimestamp(int(user_data[key]["deal"]["exit"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "sl_price": float(user_data[key]["order"]["exit"].get('sl')),
                        "tp_price": float(user_data[key]["order"]["exit"].get('tp')),
                        "swap": float(user_data[key]["deal"]["exit"]["swap"]),
                        "account_id": acc_id,
                        "trade_type": trade_type,
                    }
                    
                    # Append the trade_data to a list for the bulk create
                    trade_list.append(trade_data)
                    
            if trade_list :
                trade_hist = self.supabase.table("trade_history").insert(trade_list).execute()  
                
                if not trade_hist :
                    
                    return Return_Type(status=False, msg="Error inserting trade history", data=None)
           
                return Return_Type(status=True, msg="Success inserting trade history", data=trade_hist)
                    
            
        except Exception as e:
            return e
        
        
        

    async def store_funding_details(self, fund_data_json:dict, acc_id:int ):
        
        try:
            # Loop through and check if the funding details have been stored in the database
            fund_list =[]
           
            for data in fund_data_json:
                
                fund_info = await self.check_funding_info(acc_id,int(data))
              
                
                if fund_info:
                    continue
                    
                
                fund_det = fund_data_json[data]
                fund_type = None
                

                for info in fund_det:
                
                    if fund_det[info]["profit"] < 0 :
                        fund_type = "withdrawal"
                    else:
                        fund_type= "deposit"
                    fund_data = {
                            "position_id": int(fund_det[info]["ticket"]),
                            "entry_price": float(fund_det[info]["price"]),
                            "exit_price": None,
                            "volume": float(fund_det [info]["volume"]),
                            "commission":float(fund_det[info]["commission"]),
                            "fee": float(fund_det[info]["fee"]),
                            "profit_loss": float(fund_det[info]["profit"]),
                            "symbol": str(fund_det[info]["symbol"]),
                            "entry_time": datetime.datetime.fromtimestamp(int(fund_det[info]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                            "exit_time": None,
                            "sl_price": float(0),
                            "tp_price": float(0),
                            "swap": float(fund_det[info]["swap"]),
                            "account_id":acc_id,
                            "trade_type": fund_type,
                        }
                    
                    fund_list.append(fund_data)
                
            if not fund_list:
                 return Return_Type(status=False, msg="Error inserting funding details", data=None)
             
            fund_hist = self.supabase.table("trade_history").insert(fund_list).execute() 
            
            return Return_Type(status=True, msg="Success inserting funding details", data=fund_hist)
        
        except Exception as e:
            return e
        
           
            
    async def check_funding_info(self,acc_id:int, pos_id:int):
        try:
            funding_info = self.supabase.table("trade_history").select("*").eq("position_id",pos_id).eq("account_id",acc_id).execute()
            return funding_info.data
        except Exception as e:
            return e
        
    