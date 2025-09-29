from .db import supabase_conn 
from .model import  Return_Type


class Strategy:
    
    
    def __init__(self):
    
        self.supabase = supabase_conn()
    
    
    async def create_strategy(self,data:dict):
        
        try:
            strategy = self.supabase.table("strategy").insert(data).execute()
            return strategy.data
        except Exception as e:
            return e
    
        
    async def update_strategy(self,data:dict):
        
        try:
            strategy = self.supabase.table("strategy").upsert(data).execute()
            return strategy.data
        except Exception as e:
            return e
    
    
    async def delete_strategy(self, id:int):
        
        try:
            strategy = self.supabase.table("strategy").delete().eq("id", id).execute()
            return strategy.data
        except Exception as e:
            return e
        
    async def get_all_strategy_by_user(self,user_id:str):
        try :
            strategy = self.supabase.table("strategy").select("*").eq("user_id" , user_id).execute()
            return strategy.data
        except Exception as e:
            return e
        
    async def get_strategy_by_id(self, id:int):
        try :
            strategy = self.supabase.table("strategy").select("*").eq("id" , id).execute()
            
            if strategy.data:
                return ReturnT
            return strategy.data
        except Exception as e:
            return e
        