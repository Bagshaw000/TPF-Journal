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
            login_data: Acc_Model = Acc_Model(login=acc["account_no"],password=acc["password"], server=acc["server_name"],platform=acc["platform"])

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
        
    async def account_setup(self,user_id:str,acc:Deal_Req)-> Return_Type:
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
                                "updated_at": datetime.datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")    
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