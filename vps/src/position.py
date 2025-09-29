    # async def get_open_position(self,acc_id:str):
    #     try:
    #         # Check the last update date
            
    #         last_update = self.get_trade_account_by_id(acc_id)
            
            
    #         pass
    #     except Exception as e:
    #         return e   
from .db import supabase_conn   
from .model import Acc_Model,Return_Type
from .account import Accounts
from .mt5 import Mt5_Class
from .trade_history import Trader_History
import datetime
import requests 
import os
import json as js
from dotenv import load_dotenv
from datetime import timezone
from dateutil import parser
from fastapi.encoders import jsonable_encoder

load_dotenv()
class Position:
        
    def __init__(self):
    
        self.supabase = supabase_conn()
        self.acc = Accounts()
        self.trade_hist = Trader_History()
        self.mt5 = Mt5_Class()
    
   
    
    # This is an update version of the open position function
    '''
    This function trackk all open position for all meta trader files
    '''
    async def new_store_mt5_open_pos(self, open_pos: dict):
        try:
           
           
            # Get the id from mt5 query
            mt5_acc_id = next(iter(open_pos))
            
            account_val = open_pos[mt5_acc_id]
            server = account_val["server"]
            acc_pos_dict = account_val["position"]
            
            # An array to store  all position that are being migrated to the tradeHistory
            update_trade_hist_arr = []
            
            # Array of all the open position that have been migrated to the trade history table to be deleted
            del_open_trade_arr = []
            
            # Array to update open position that are in the open position database
            update_open_pos_arr = []
           
            # Get all the open position in the database for that particular 
            
            get_acc_id = await self.acc.check_account_exist(mt5_acc_id,"mt5",server)
            acc_id = get_acc_id[0]["id"]
            all_acc_open_pos_db = await self.get_mt5_open_trade_acc_id(acc_id)
            
            
            # Loop through all the trades from the database and check if they are in the new ope positions form mt5
            for pos in all_acc_open_pos_db:
                
                # Position id of open position in the database
                pos_id = pos["position_id"]
                
                
                # All open positions from mt5
                
                if pos_id in acc_pos_dict:
                   
                    # Update the position that are still ongoing position that are in the open position table and mt5 open position
                    
                    trade_data:dict= pos
                   
                    trade_data["current_price"] = account_val["position"][pos_id]["price_current"]
                    trade_data["commission"] = account_val["position"][pos_id].get("commission")
                    trade_data["fee"] = account_val["position"][pos_id].get("fee")
                    trade_data["profit_loss"] = account_val["position"][pos_id]["profit"]
                    trade_data["sl_price"] = account_val["position"][pos_id].get("sl")
                    trade_data["tp_price"] = account_val["position"][pos_id].get("tp")
                    trade_data["swap"] = account_val["position"][pos_id].get("swap")
                    
                    # Append the new data to update array
                    update_open_pos_arr.append(trade_data)
                    
                    
                else:
                    # Check if the db position id not in the mt5 open positions already been added to trade history
                    check_pos_in_trade_hist = await self.trade_hist.get_mt5_trade_history_by_acc(acc_id,pos_id )
                    # print(check_pos_in_trade_hist)
                    
                    
                    if not check_pos_in_trade_hist:
                        
                      
                        # Get the trade information from mt5 create an object and append to a list for bulk update
                        # Append the open position id to and array for mass delete
                        
                        acc_det = Acc_Model(login=mt5_acc_id,password=get_acc_id[0]['password'],server=server,timeout=None,platform="mt5",)
                     
                        comp_trade_data = await self.mt5.get_deal_by_pos_id(pos_id,acc_det)
                        
                        # Check the trades are still completed
                        if comp_trade_data["order"]["exit"] != None and comp_trade_data["deal"]["exit"] != None:
                            
                            # Map ther trade history data
                            trade_data = {
                                "position_id": int(pos_id),
                                "entry_price": float(comp_trade_data["deal"]["entry"]["price"]),
                                "exit_price": float(comp_trade_data["deal"]["exit"]["price"]),
                                "volume": float(comp_trade_data["deal"]["entry"]["volume"]),
                                "commission":float(comp_trade_data["deal"]["exit"]["commission"]),
                                "fee": float(comp_trade_data["deal"]["exit"]["fee"]),
                                "profit_loss": float(comp_trade_data["deal"]["exit"]["profit"]),
                                "symbol": str(comp_trade_data["deal"]["exit"]["symbol"]),
                                "entry_time": datetime.datetime.fromtimestamp(int(comp_trade_data["deal"]["entry"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                "exit_time": datetime.datetime.fromtimestamp(int(comp_trade_data["deal"]["exit"]["time_msc"])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                                "sl_price": (comp_trade_data["order"]["exit"].get('sl')),
                                "tp_price": (comp_trade_data["order"]["exit"].get('tp')),
                                "swap": float(comp_trade_data["deal"]["exit"]["swap"]),
                                "account_id": acc_id,
                                "trade_type":pos["trade_type"] ,
                                "emotion_tag":pos["emotion_tag"],
                                "pre_trade_note": pos["pre_trade_note"],
                                "pos_trade_note": pos["pos_trade_note"],
                                "trade_images": pos["trade_images"]
                            }
                            
                            # Append to the update trade history array and append to the delete open position array to delete the closed position from open trade table
                            update_trade_hist_arr.append(trade_data)
                            del_open_trade_arr.append(pos["id"])
                           
                    else:
                     
                        # This is for trades that are in open position table and trade history just need to delete form open position table
                        del_open_trade_arr.append(pos["id"])
                     
            
            # Perform all the update delete in the open position and trade history table
            
            # This activate when you are moving trades
            if update_trade_hist_arr and del_open_trade_arr:
                update_trade = await self.trade_hist.insert_trade(update_trade_hist_arr)
                
                if update_trade:
                    await self.delete_many_open_pos(del_open_trade_arr) 
                    
            
            # This only activates when the trade is already in tradehistory and need no update
            if del_open_trade_arr :
                await self.delete_many_open_pos(del_open_trade_arr)    
            
            #  This update old position that are still open in the database
            if update_open_pos_arr:
                await self.update_open_pos(update_open_pos_arr)
            
            # Store the new open position 
            new_open_position = []
            # For all open position trade that are new add them to the open position table 
            for pos in acc_pos_dict:
                # Loop through all the open position check if they are not in open position and trade history 
                check_in_open_pos = await self.get_mt5_open_trade_pos_id_acc_id(acc_id,int(pos))
               
                # Confirm the new position is not in the open trade database   
                if not check_in_open_pos:
                    
                    # Determine the trade type
                    trade_type = None
                    if acc_pos_dict[pos]["type"] == 0:
                        trade_type = "buy"
                    elif acc_pos_dict[pos]["type"] == 1:
                        trade_type = "sell"
                        
                    # Map the new position data
                    pos_dat = {
                        "position_id" :  int(pos) ,
                        "entry_price": float(acc_pos_dict[pos]['price_open']),
                        "current_price":float(acc_pos_dict[pos]['price_current']),
                        "volume":float(acc_pos_dict[pos]['volume']),
                        "commission":(acc_pos_dict[pos].get('commission')),
                        "fee":(acc_pos_dict[pos].get('fee')),
                        "profit_loss":float(acc_pos_dict[pos]['profit']),
                        "symbol":str(acc_pos_dict[pos]['symbol']),
                        "sl_price":(acc_pos_dict[pos].get('sl')),
                        "tp_price":(acc_pos_dict[pos].get('tp')),
                        "swap":float(acc_pos_dict[pos]['swap']),
                        "trade_type":str(trade_type), 
                        "account_id":int(acc_id),
                        "platform":"mt5",
                        "server_name":str(server),
                        "updated_at":datetime.datetime.fromtimestamp(int(acc_pos_dict[pos]['time_update_msc'])/1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "entry_time":datetime.datetime.fromtimestamp(int(acc_pos_dict[pos]['time_msc'])/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                    }
                    
                    # Append to the new position insert list
                    new_open_position.append(pos_dat)
                    
                else:
                    continue 
                
            if new_open_position:
                await self.insert_open_trade(new_open_position)
                         
        except Exception as e:
             return e

    '''
    The function makes sure the user data history is up to date
    '''
    
    async def get_all_user_last_trade(self, acc):
        
        
        # Create an empty list that will be used to add all trades to update user account
        trade_list = []
        
        # Assign the trade type to None this will be reassigned later on 
        trade_type = None
        
        # Get the last trade for this particular account
        acc_det = await self.trade_hist.get_user_last_trade_entry_time(acc_id=acc["id"])
        
        # Check any information is return 
        if not acc_det:
          return
        
        # Get the time of the last trade
        trade_time =datetime.datetime.strptime(acc_det[0]['entry_time'], "%Y-%m-%dT%H:%M:%S.%f").astimezone(tz=timezone.utc)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Check if the trade time is less than current time
        if trade_time < now:
            
            # Get the user login data
            login_data: Acc_Model = Acc_Model(login=acc["account_no"],password=acc["password"], server=acc["server_name"],platform=acc["platform"])

            # Check if any trade occurred within that period
            trade_hist_data = await self.mt5.get_deal_history(trade_time.replace(tzinfo=None),now.replace(tzinfo=None), login_data)
            
            # Check if any trade occured between that period
            if not trade_hist_data :
        
                return {
                    "status":200,
                    "msg": "No trade occurred within this period",
                }
            
            # If trades exist then loop through
            for key in trade_hist_data:
                
                # Check if it a completed trade by confirming the exit for both the deal and order
                if trade_hist_data[key]["order"]["exit"] == None and trade_hist_data[key]["deal"]["exit"] == None:
                   
                    continue
                
                # Incase the Entry deal or order was created before the last trade entry time get the coressponding deal and position data for the entry position
                if trade_hist_data[key]["order"]["entry"] == None:
                    order_info =await self.mt5.get_order_by_pos_id(pos_id=key,account=login_data)
                   
                    if order_info != None:
                        
                        trade_hist_data[key]["order"]["entry"] = order_info
                        
                if trade_hist_data[key]["deal"]["entry"] == None:
                    deal_info =await self.mt5.get_deal_by_pos_id(pos_id=key, account=login_data)
                  
                    if deal_info != None:
                        trade_hist_data[key]["deal"]["entry"] = order_info
                
                
                
                # Check if the trade posision id attached to these account details  are in the database to avoid duplicate 
                pos_in_db = await self.trade_hist.get_mt5_trade_history_by_acc(acc["id"],key)
              
                
                # If it is in data base then dont add
                if pos_in_db:
                    
                    continue
                
                # Check if the trade type is buy or sell
                if trade_hist_data[key]["deal"]["entry"]["type"] == 0:
                    trade_type = "buy"
                elif trade_hist_data[key]["deal"]["entry"]["type"] == 1:
                    trade_type = "sell"

              
                # Get the data if it is in position table to confirm it and ongoing trade that was completed
                pos_data = await self.get_mt5_open_trade_pos_id_acc_id(pos_id=int(key),acc_id=int(acc["id"]),server=acc["server_name"])

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
                            "trade_type": trade_type,}
                
                # If trader was in the open position table then you 
                if (len(pos_data)>0):
                    pos_info = {
                            "emotion_tag":pos_data[0]["emotion_tag"] | None,
                            "pre_trade_note": pos_data[0]["pre_trade_note"]  | None,
                            "pos_trade_note": pos_data[0]["pos_trade_note"] | None,
                            "trade_images": pos_data[0]["trade_images"]  | None
                        }
                    # Update the trad details
                    trade_data.update(pos_info)
                
                
                # Append trade to trade list
                trade_list.append(trade_data)
                    
            
            # Insert all trade history into the database
            if len(trade_list)>0:
               
                updated = await self.trade_hist.insert_trade(trade_list)
                return  {
                            "status":200,
                            "msg": "Successfully updated the accpunt history",
                            "data": updated
                        }
            # If no update is needed
            return {
                "status":200,
                "msg": "No update required",
            }
        # Rare case where it never happens when the last trade entry time is larger than current time
        return {
            "status":200,
            "msg": "No update needed >",
                            
        }
    
    '''
    Insert one or many trade in to the open trade table
    '''      
    async def insert_open_trade(self, data):
        try:
            open_pos = self.supabase.table("open_trade").insert(data).execute()
        
            return open_pos.data
        except Exception as e:
            return e     
        
    
    '''
    Get all open trade attached to a particular mt5 acount
    '''   
    async def get_mt5_open_trade_acc_id(self, acc_id:int):
        try:
            open_pos = self.supabase.table("open_trade").select('*').eq('account_id', acc_id).eq("platform","mt5").execute()
            
            return open_pos.data
        except  Exception as e:
            return e
    
    
    '''
    Get all open trade by mt5 position id and account id
    '''   
    async def get_mt5_open_trade_pos_id_acc_id(self, acc_id:int,pos_id:int):
        try:
            open_pos = self.supabase.table("open_trade").select('*').eq('account_id', acc_id).eq('position_id', pos_id).eq("platform","mt5").execute()
            
            return open_pos.data
        except  Exception as e:
            return e
        
   
    '''
    Update position from open trade database
    '''    
    async def update_open_pos(self, data:list, pos_id:int):
        try:
            
            check = await self.check_pos(pos_id)
            
            if check.status == True:
                open_pos = self.supabase.table("open_trade").upsert(data).execute()
                
                return  Return_Type(status=True,msg="success", data=open_pos.data)
            
            open_pos = await self.trade_hist.update_trade(data)
            
            if open_pos.data:
                return  Return_Type(status=True,msg="success", data=open_pos.data)
            
            return Return_Type(status=False,msg="fail",data=None)
        except Exception as e:
            return e 
    
    async def check_pos(self, pos_id:int):
        try: 
            pos = self.supabase.table("open_trade").select(count= "exact").eq("id",pos_id).execute()
            
            if pos.count > 0:
                return Return_Type(status=True,msg="success",data=None)
            
            return Return_Type(status=False,msg="fail",data=None)
        except Exception as e:
            return e
    
    '''
    Delete  one position from open trade database
    '''
    async def delete_open_pos(self, id:int):
        try:
            open_pos = self.supabase.table("open_trade").delete().eq("id", id).execute()
            return open_pos.data
        except Exception as e:
            return e 
    
    '''
    Delete  many position from open trade database
    '''
    async def delete_many_open_pos(self, id:list):
        try:
            open_pos = self.supabase.table("open_trade").delete().in_("id", id).execute()
            return open_pos.data
        except Exception as e:
            return e 
     