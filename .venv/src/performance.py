from .db import supabase_conn        
from datetime import datetime                                                                                                                                                                                                                                                                                                                                                                                     
class Performance:
    
    def __init__(self):
    
        self.supabase = supabase_conn()
        
    async def gross_profit(self, acc_id:int):
        try:
            gross = self.supabase.table("trade_history").select("profit_loss ").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            gross_profit = 0
            for data in gross.data:
                if data["profit_loss"]>1:
                    gross_profit = gross_profit + data["profit_loss"]
            return gross_profit
        except Exception as e :
            return e
        
    async def gross_loss(self, acc_id:int):
        try:
            gross = self.supabase.table("trade_history").select("profit_loss ").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            gross_loss = 0
            for data in gross.data:
                if data["profit_loss"]< -1:
                    gross_loss = gross_loss + data["profit_loss"]
            return gross_loss
        except Exception as e :
            return e
        
    async def net_profit(self, acc_id:int):
        try:
            net_profit = await self.gross_profit(acc_id) -  await self.gross_loss(acc_id)
            return net_profit
        except Exception as e:
            return e
        
    async def total_return(self, acc_id:int):
        try:
            initial_capital = self.supabase.table("accounts").select("initial_capital").eq("account_id", acc_id).execute()
            total_return = (await self.net_profit(acc_id)/initial_capital) * 100
            
            return total_return
        except Exception as e:
            return e
    
    async def avg_return_per_trade(self, acc_id:int):
        try:
            count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).execute()
            avg_return_per_trade = (await self.net_profit(acc_id))/count
            
            return avg_return_per_trade
        except Exception as e:
            return e
    
    
    async def percent_winning_trade(self, acc_id:int):
        try:
            trade = self.supabase.table("trade_history").select("profit_loss ").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            count = 0
            
            for data in trade.data:
                if data["profit_loss"]>1:
                    count = count + 1
            
            percent_win = (count/ len(trade.data)) * 100
            
            return percent_win
        except Exception as e:
            return e
        
    async def percent_losing_trade(self, acc_id:int):
        try:
            trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            count = 0
            
            for data in trade.data:
                if data["profit_loss"]<-1:
                    count = count + 1
            
            percent_win = (count/ len(trade.data)) * 100
            
            return percent_win
        except Exception as e:
            return e


    async def win_loss_ration(self,acc_id:int):
        try:
            ratio = await self.percent_winning_trade(acc_id) / await self.percent_losing_trade(acc_id)
            return ratio
        except Exception as e:
            return e
        
    async def avg_trade_duration(self, acc_id:int):
        try:
            time = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            avg_duration = 0
            
            for idx, data in enumerate(time.data):

                entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                
                time_diff = exit - entry

                if idx == 0:
                    avg_duration = time_diff
                else:
                    avg_duration = (avg_duration + time_diff)/2
            
            
            return avg_duration
        except Exception as e:
            return e
        
        
    async def avg_loss_trade_duration(self, acc_id:int):
        try:
            time = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            avg_duration = 0
            
            for idx, data in enumerate(time.data):
                if data["profit_loss"]<-1:
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
            
            
            return avg_duration
        except Exception as e:
            return e
        
    async def avg_win_trade_duration(self, acc_id:int):
        try:
            time = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            avg_duration = 0
            
            for idx, data in enumerate(time.data):
                if data["profit_loss"]>1:
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
            
            
            return avg_duration
        except Exception as e:
            return e