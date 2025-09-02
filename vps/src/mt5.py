from .model import Acc_Model, Account_Info, MT5_Deal, MT5_Order,Deal_Req
import MetaTrader5 as mt5
from datetime import datetime
from collections import defaultdict
from .db import supabase_conn
from typing import Dict
import json

class Mt5_Class:
    
    
    def __init__(self):
        self.supabase = supabase_conn()
        
    
    '''
    This function setup the user trading account
    '''
    async def setup_Account(self,data:Deal_Req):
        try:
            authorized = mt5.login(data.login,password=data.password,server=data.server)
             
            if authorized:
                
                to_date = datetime.now()

                # Improve thei from being hardcoded to be dynamic
                from_date = datetime(2015,1,1)
            
                
                user_trading_data = await self.get_deal_history(from_date, to_date, data)
                
                
            return user_trading_data
        except Exception as e:
            return e
    
    '''
        This function gets the user order history
    '''   
    async def get_order_history(self, from_date, to_date):
        try:
            # Get order history
            history_orders = mt5.history_orders_get(from_date, to_date)
            order_info_dict = defaultdict(dict)
            
           
            # Map each order to its order ticket  
            for order in history_orders:
                order_info_dict[order._asdict()["ticket"]] = order._asdict()      
                    
            return order_info_dict
        except Exception as e:
            return e
    
    '''
        This get the deal history of the account
    '''
    async def get_deal_history(self, from_date, to_date, data:Acc_Model):
        try:
            # Get the user deal history
            authorized = mt5.login(data.login,password=data.password,server=data.server)
             
            if authorized:
                history_deals: list[MT5_Deal] = mt5.history_deals_get(from_date, to_date)
                
                # Get the user order hisotry
                order_data= await self.get_order_history(from_date,to_date)
            
                
                # Create a dummy object to hold both order and deal that are related by deal.order and order.ticket    
                deal_posid_dict = defaultdict(lambda: {
                "order": {"entry": None, "exit": None},
                "deal": {"entry": None, "exit": None}
                })
                
                # Object to store the funding details
                # funding_withdraw = defaultdict()
                
                
                
                for deal in history_deals:
                    
                    # Check if the deal is a funding or withdrawal action if so skip it
                    if int(deal.order) == 0 or int(deal.position_id) == 0:
                    
                        continue
                    # Check if the order ticket that created the deal is in the order data if not skip
                    if deal.order not in order_data:
                        continue
                    
                        
                    '''
                        Check the deal entry type
                        for each entry type get the order associated with that deal creation 
                        for this association 
                            "deal.order = order.ticket"
                        Once the association is created then store the order and deal info based on the position id and 
                        entry type entry or exit
                    '''
                    
                    
                    match deal.entry:
                        case 0:  # Entry
                            deal_posid_dict[deal.position_id]["order"]["entry"] = order_data[deal.order]
                            deal_posid_dict[deal.position_id]["deal"]["entry"] = deal._asdict()

                        case 1:  # Exit
                            deal_posid_dict[deal.position_id]["order"]["exit"] = order_data[deal.order]
                            deal_posid_dict[deal.position_id]["deal"]["exit"] = deal._asdict()
                # Factor in depositi and withdrawal from the account
                # print(funding_withdraw)
                # print(deal_posid_dict)   
            return deal_posid_dict
        except Exception as e:
            return e
        
    '''
    This function is to get the metatrader account details
    '''   
    async def get_account_details(self,data:Acc_Model):
        
        try:
            authorized = mt5.login(data.login,password=data.password,server=data.server)
                
            if authorized:
                acc_info = mt5.account_info()._asdict()
                return acc_info
        except Exception as e:
            return e
    

        
    # async def store_funding_details()
    
     
    
    '''
    Get all open position for a particular account
    '''    
    async def get_open_position(self, account:Acc_Model):
        try:
            # Create an empty dictionary 
            users_open_position = defaultdict(
                lambda:{
                    "server": None,
                    "position": defaultdict(dict)
                }
            )
            
            #Login user into the mt5 account
            authorized = mt5.login(account.login,password=account.password,server=account.server)
            
            #If the account is logged in
            if authorized:
                
                #Get all the open position 
                open_pos = mt5.positions_get()
                
                users_open_position[account.login]['server'] = account.server
                #Map all position to the account in the empty dictionary
                for pos in open_pos:
                 
                    users_open_position[account.login]['position'][pos._asdict()['ticket']] = pos._asdict()  
                  
            return users_open_position       
            
        except Exception as e:
            return e
        
    '''
     This get deal by position id 
    '''   
    async def get_deal_by_pos_id(self, pos_id:int):
        try:
            
            deal_list:list[MT5_Deal]  = mt5.history_deals_get(position=pos_id)
            order = await self.get_order_by_pos_id(pos_id)
            deal_posid_dict = {
                "order": {"entry": None, "exit": None},
                "deal": {"entry": None, "exit": None}
            }
            
            for deal in deal_list:
                match deal.entry:
                    case 0:  # entry
                        deal_posid_dict["deal"]["entry"] = deal._asdict()
                        deal_posid_dict["order"]["entry"] = order.get(deal.order)
                    case 1:  # exit
                        deal_posid_dict["deal"]["exit"] = deal._asdict()
                        deal_posid_dict["order"]["exit"] = order.get(deal.order)
                    
                
            return deal_posid_dict
        except Exception as e:
            return e

    '''
     This get deal by position id 
    '''   
    async def get_order_by_pos_id(self, pos_id:int):
        try:
            order_list: list[MT5_Order] = mt5.history_orders_get(position=pos_id)
            order_dict = defaultdict(lambda:dict)
            
            for order in order_list:
                order_dict[order.ticket] = order._asdict()
                
            return order_dict
        except Exception as e:
            return e
        
    '''
    This function get all the user funding data
    '''
    async def get_funding_details(self,data:Deal_Req, acc_id:int):
        
        try:
            # Get the current date to be used to get the recent funding information
            to_date = datetime.now()
            
            
            # Login the user into mt5
            authorized = mt5.login(data.login,password=data.password,server=data.server)
            
            # This dictionary will hold all the funding information
            funding_dict = defaultdict(lambda:defaultdict(
                lambda:{}
            ))
            
            #Confirm the the user login is correct
            if authorized:
                # acc_det = await self.get_account_det(data.login,data.password,data.server)
            
                
                # Get all the user deals
                funding_det:list[MT5_Deal] = mt5.history_deals_get(data.from_, to_date)
               
                # if acc_det and len(acc_det) > 0:          
                # Loops through all the deal
                for det in funding_det:
                    
                    
                    # Finds the funding details byt deal type and updated the funding detail dictionary
                    if int(det.type) == 2:
                      
                        funding_dict[acc_id][det.ticket] = det._asdict()
                    
           
            return funding_dict
            
        except Exception as e:
            return e 
    
    async def get_account_det(self, acc_no:int, password:str, server:str):
        try:
            # limit to one
            acc_det = self.supabase.table("accounts").select("*").eq("account_no", acc_no).eq("password", password).eq("server_name",server).eq("platform","mt5").execute()
            return acc_det.data
        except Exception as e:
            return e