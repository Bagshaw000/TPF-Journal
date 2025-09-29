from .db import supabase_conn   
from .account import Accounts
import requests 
import os
import json as js
import datetime
from dotenv import load_dotenv
load_dotenv()
class Trader_History:
    
    def __init__(self):
    
        self.supabase = supabase_conn()
        self.acc = Accounts()
    
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
    
    async def update_trade(self, data):
        try:
            
            trade_hist = self.supabase.table("trade_history").upsert(data).execute()
            return trade_hist
        except Exception as e:
            return e
    async def get_user_last_trade(self,acc_id):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).order('exit_time', desc=True).limit(1).execute()
            return trade_hist.data
        except Exception as e:
            return e
    
    '''
    This function gets the user last trade
    '''
    async def get_user_last_trade_entry_time(self,acc_id):
        try:
            trade_hist = self.supabase.table("trade_history").select('*').eq("account_id",acc_id).order('entry_time', desc=True).limit(1).execute()
            return trade_hist.data
        except Exception as e:
            return e
        
    