from .model import Mt5_Model, Account_Info, MT5Deal, MT5Order
import MetaTrader5 as mt5
from datetime import datetime
from collections import defaultdict
from typing import Dict
import json

class Mt5_Action:
    
    '''
    This function setup the user trading account
    '''
    async def setup_Account(self,data:Mt5_Model):
        try:
            authorized = mt5.login(data.login,password=data.password,server=data.server)
            
                
            if authorized:
                
                to_date = datetime.now()
                # print(to)
                from_date = datetime(2015,1,1)
            
                
                user_trading_data = await self.get_deal_history(from_date, to_date)
                
               
        
                
                
                
            # mt5.shutdown()
       
            return user_trading_data.items()   
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
        
    async def get_deal_history(self, from_date, to_date):
        try:
            # Get the user deal history
            history_deals: list[MT5Deal] = mt5.history_deals_get(from_date, to_date)
            
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
                    # if int(deal.position_id) == 0:
                    #     funding_withdraw[deal.ticket] = deal._asdict() 
                    continue
                # Check if the order ticket that created the deal is in the order data if not skip
                if deal.order not in order_data:
                    continue
                    # print(deal.position_id)
                    
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
                     
            return deal_posid_dict
        except Exception as e:
            return e
    
    
    