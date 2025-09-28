from .db import supabase_conn        
from datetime import datetime  
import json
# import datetime
from src.utils import get_past_date
 
time_period = {
    "y": 1,
    "t-w": 7,
    "l-w": 14,
    "t-m": 30,
    "l-m": 60,
    "3-m": 90,
    "6-m": 183,
    "12-m":365,
}                                                                                                                                                                                                                                                                                                                                                                                 
class Performance:
 
    def __init__(self):
    
        self.supabase = supabase_conn()
        
    
    # This function measure gross profit for the user accounts 
    async def gross_profit(self, acc_id:int, time="*"):
        try:
            if time == "*":
                gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gt("profit_loss",0).execute()
                long_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","buy").gt("profit_loss",0).execute()
                short_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","sell").gt("profit_loss",0).execute()
                
                gross_profit = 0
                long_profit = 0
                short_profit = 0
                for data in gross.data:
                    gross_profit = gross_profit + data["profit_loss"]
                        
                for data in long_trades_gross.data:
                    long_profit = long_profit + data["profit_loss"]
                        
                for data in short_trades_gross.data:
                    short_profit = short_profit + data["profit_loss"]
                    
                return {
                    "total": gross_profit,
                    "long": long_profit,
                    "short": short_profit
                }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
             
                
                gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","buy").gte("entry_time",past_date).gt("profit_loss",0).execute()
                short_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","sell").gte("entry_time",past_date).gt("profit_loss",0).execute()
                
                gross_profit = 0
                long_profit = 0
                short_profit = 0
                for data in gross.data:
                    gross_profit = gross_profit + data["profit_loss"]
                        
                for data in long_trades_gross.data:
                    long_profit = long_profit + data["profit_loss"]
                        
                for data in short_trades_gross.data:
                    short_profit = short_profit + data["profit_loss"]
                        
                return {
                    "total": gross_profit,
                    "long": long_profit,
                    "short": short_profit
                }
                
                
        except Exception as e :
            return e
    
    # This function measure gross loss for the trading account
    async def gross_loss(self, acc_id:int, time="*"):
        try:
            if time == "*":
                gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").lt("profit_loss",0).execute()
                long_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","buy").lt("profit_loss",0).execute()
                short_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","sell").lt("profit_loss",0).execute()
                
                gross_profit = 0
                long_profit = 0
                short_profit = 0
                for data in gross.data:
                    gross_profit = gross_profit + data["profit_loss"]
                        
                for data in long_trades_gross.data:
                    long_profit = long_profit + data["profit_loss"]
                        
                for data in short_trades_gross.data:
                    short_profit = short_profit + data["profit_loss"]
                        
                return {
                    "total": gross_profit,
                    "long": long_profit,
                    "short": short_profit
                }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","buy").gte("entry_time",past_date).lt("profit_loss",0).execute()
                short_trades_gross = self.supabase.table("trade_history").select("profit_loss").eq("account_id", acc_id).eq("trade_type","sell").gte("entry_time",past_date).lt("profit_loss",0).execute()
                
                gross_profit = 0
                long_profit = 0
                short_profit = 0
                for data in gross.data:
                    gross_profit = gross_profit + data["profit_loss"]
                        
                for data in long_trades_gross.data:
                    long_profit = long_profit + data["profit_loss"]
                        
                for data in short_trades_gross.data:
                    short_profit = short_profit + data["profit_loss"]
                        
                return {
                    "total": gross_profit,
                    "long": long_profit,
                    "short": short_profit
                }
        except Exception as e :
            return e
    
    # This function calculate the net profit from the user accounts 
    async def net_profit(self, acc_id:int, time="*"):
        try:
            gross_profit = await self.gross_profit(acc_id, time)
            gross_loss =  await self.gross_loss(acc_id,time)
         
            net_profit = gross_profit["total"] + gross_loss["total"]
            long_net_profit = gross_profit["long"] + gross_loss["long"]
            short_net_profit = gross_profit["short"] + gross_loss["short"]
            return {
                    "total": net_profit,
                    "long": long_net_profit,
                    "short": short_net_profit
                }
        except Exception as e:
            return e
    
    # This function provides the total return for that account
    async def percent_total_return(self, acc_id:int , time="*"):
        try:
            initial_capital = self.supabase.table("accounts").select("initial_capital").eq("id", acc_id).execute()
            net_profit = await self.net_profit(acc_id, time)
            total_return = ((net_profit['total'])/initial_capital.data[0]["initial_capital"]) * 100
            long_return = (net_profit['long']/initial_capital.data[0]["initial_capital"]) * 100
            short_return = (net_profit['short']/initial_capital.data[0]["initial_capital"]) * 100
            
            return {
                    "total": total_return,
                    "long": long_return,
                    "short": short_return
                }
        except Exception as e:
            return e
    
    # This function shows average return per trade
    async def avg_return_per_trade(self, acc_id:int, time="*"):
        try:
            count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
            net_profit = await self.net_profit(acc_id,time)
            
            if count.count == 0:
                return {
                    "total": 0,
                    "long": 0,
                    "short": 0
                } 
            avg_return_per_trade = (net_profit["total"])/count.count 
            avg_return_per_long = (net_profit["long"])/count.count
            avg_return_per_short = (net_profit["short"])/count.count
            
            return {
                    "total": avg_return_per_trade,
                    "long": avg_return_per_long,
                    "short": avg_return_per_short
                }
        except Exception as e:
            return e
    
    # This function shows the percentage win rate of that account
    async def percent_winning_trade(self, acc_id:int, time="*"):
        try:
            
            if time == "*":
                count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gt("profit_loss",0).execute()
                long_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gt("profit_loss",0).execute()
                short_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gt("profit_loss",0).execute()
                    
                
                percent_win = (trade.count/ count.count) * 100 if count.count else 0
                long_percent_win = ((long_trade.count)/ (trade.count)) * 100 if trade.count else 0
                short_percent_win = ((short_trade.count)/ (trade.count)) * 100 if trade.count else 0
                
                return {
                    "total": percent_win,
                    "long": long_percent_win,
                    "short": short_percent_win
                }
            else: 
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).gt("profit_loss",0).execute()
                long_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).gt("profit_loss",0).execute()
                short_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).gt("profit_loss",0).execute()
                
              
                
                percent_win = (trade.count/ count.count) * 100 if count.count else 0
                long_percent_win = ((long_trade.count)/ (trade.count)) * 100 if trade.count else 0
                short_percent_win = ((short_trade.count)/ (trade.count)) * 100 if trade.count else 0
                
                return {
                    "total": percent_win,
                    "long": long_percent_win,
                    "short": short_percent_win
                }
        except Exception as e:
            return e
    
    # This function shows the percentage loss rate of that account   
    async def percent_losing_trade(self, acc_id:int, time="*"):
        try:
           
            if time == "*":
                count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").lt("profit_loss",0).execute()
                long_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "buy").lt("profit_loss",0).execute()
                short_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "sell").lt("profit_loss",0).execute()
                
                percent_loss = (trade.count/ count.count) * 100 if count.count else 0
                long_percent_loss =  ((long_trade.count)/ (trade.count)) * 100 if trade.count else 0
                short_percent_loss = ((short_trade.count)/ (trade.count)) * 100 if trade.count else 0
                return {
                    "total": percent_loss,
                    "long": long_percent_loss,
                    "short": short_percent_loss
                }
            else: 
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                count = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).lt("profit_loss",0).execute()
                long_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).lt("profit_loss",0).execute()
                short_trade = self.supabase.table("trade_history").select(count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).lt("profit_loss",0).execute()
                
                percent_loss = (trade.count/ count.count) * 100 if count.count else 0
                long_percent_loss =  ((long_trade.count)/ (trade.count)) * 100 if trade.count else 0
                short_percent_loss = ((short_trade.count)/ (trade.count)) * 100 if trade.count else 0
                
                return {
                    "total": percent_loss,
                    "long": long_percent_loss,
                    "short": short_percent_loss
                }
        except Exception as e:
            return e

   

    # This function shows the win loss ratio Profit factor Revist this
    async def cal_profit_factor(self,acc_id:int, time="*"):
        try:
            percent_win = await self.percent_winning_trade(acc_id, time)
            percent_loss = await self.percent_losing_trade(acc_id,time)
          
            
            return {
            "total": self.profit_factor(float(percent_win["total"]), float(percent_loss["total"])),
            "long": self.profit_factor(float(percent_win["long"]), float(percent_loss["long"])),
            "short": self.profit_factor(float(percent_win["short"]), float(percent_loss["short"]))
             }
        except Exception:
            return {"total": 0.0, "long": 0.0, "short": 0.0}
            
    def profit_factor(self,gross_profit: float, gross_loss: float) -> float:
        try:
     
            gross_loss = abs(gross_loss)

            # No trades
            if gross_profit == 0 and gross_loss == 0:
                return 0.0

            # No losses but profit → PF = ∞
            if gross_loss == 0:
                # return float("inf") if gross_profit > 0 else 0.0
                return gross_profit if gross_profit > 0 else 0.0

            return gross_profit / gross_loss
        except Exception as e:
            return 0.0
    
    
    # This function shows the average duration per trade
    async def avg_trade_duration(self, acc_id:int, time="*"):
        try:
            if time == "*":
                trades = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                long_trade = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").execute()
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                
                for idx, data in enumerate(trades.data):

                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                
                trades = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trade = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).execute()
                
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                
                for idx, data in enumerate(trades.data):

                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
        except Exception as e:
            return e
        
    # # This function shows the average loss duration
    async def avg_loss_trade_duration(self, acc_id:int, time="*"):
        try:
            if time == "*":
                
                trades = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").lt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").lt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").lt("profit_loss", 0).execute()
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                 
                
                for idx, data in enumerate(trades.data):
                   
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                print(str(avg_duration))
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
               
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trades = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                
                for idx, data in enumerate(trades.data):
                 
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
        except Exception as e:
            return e
    
    # # This function shows the average win duration  
    async def avg_win_trade_duration(self, acc_id:int, time="*"):
        try:
            if time == "*":
                
                trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").gt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").gt("profit_loss", 0).execute()
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                 
                
                for idx, data in enumerate(trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                            
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss","entry_time","exit_time").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                
                
                
                avg_duration = 0
                long_avg_duration = 0
                short_avg_duration = 0
                
                for idx, data in enumerate(trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        avg_duration = time_diff
                    else:
                        avg_duration = (avg_duration + time_diff)/2
                
                
                for idx, data in enumerate(long_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        long_avg_duration = time_diff
                    else:
                        long_avg_duration = (avg_duration + time_diff)/2
                
                for idx, data in enumerate(short_trade.data):
                    
                    entry = datetime.fromisoformat(data["entry_time"]).replace(tzinfo=None)
                    exit = datetime.fromisoformat(data["exit_time"]).replace(tzinfo=None)
                    
                    time_diff = exit - entry

                    if idx == 0:
                        short_avg_duration = time_diff
                    else:
                        short_avg_duration = (avg_duration + time_diff)/2
                
                
                return {
                    "total": str(avg_duration),
                    "long": str(long_avg_duration),
                    "short": str(short_avg_duration)
                }
                
        except Exception as e:
            return e
        
    async def get_total_trades(self, acc_id:int, time="*"):
        try:
            
            if time == "*":
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").execute()
                
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).execute()
                
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
        except Exception as e:
            return e
        
    async def get_total_win_trades(self, acc_id:int, time="*"):
        try:
            
            if time == "*":
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gt("profit_loss", 0).execute()
                
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
                
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).gt("profit_loss", 0).execute()
                
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
                
        except Exception as e:
            return e
        
    async def get_total_loss_trades(self, acc_id:int, time="*"):
        try:
            
            if time == "*":
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").lt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").lt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").lt("profit_loss", 0).execute()
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                long_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "buy").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                short_trade = self.supabase.table("trade_history").select("*",count="exact").eq("account_id", acc_id).eq("trade_type", "sell").gte("entry_time",past_date).lt("profit_loss", 0).execute()
                
                return {
                    "total": trade.count,
                    "long": long_trade.count,
                    "short": short_trade.count
                    }
        except Exception as e:
            return e
        
    '''
    This function gets the total sum of the lots traded
    '''   
    async def traded_lot(self, acc_id:int, time="*"):
        try:
            if time == "*":
                trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                long_trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).eq("trade_type", "sell").execute()
                
                return {
                    "total":  sum(row["volume"] for row in trade.data),
                    "long": sum(row["volume"] for row in long_trade.data),
                    "short": sum(row["volume"] for row in short_trade.data)
                    }
             
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                
                trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("volume").eq("account_id",acc_id).eq("trade_type", "sell").gte("entry_time",past_date).execute()
                
                return {
                    "total":  sum(row["volume"] for row in trade.data),
                    "long": sum(row["volume"] for row in long_trade.data),
                    "short": sum(row["volume"] for row in short_trade.data)
                    }
        except Exception as e:
            return e
        
    async def total_commission(self, acc_id:int, time="*"):
        try:
            if time == "*":
                trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").execute()
                long_trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).eq("trade_type", "sell").execute()
                
                return {
                    "total":  sum(row["commission"] for row in trade.data),
                    "long": sum(row["commission"] for row in long_trade.data),
                    "short": sum(row["commission"] for row in short_trade.data)
                    }
             
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                
                trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).or_("trade_type.eq.sell, trade_type.eq.buy").gte("entry_time",past_date).execute()
                long_trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("commission").eq("account_id",acc_id).eq("trade_type", "sell").gte("entry_time",past_date).execute()
                
                return {
                    "total":  sum(row["commission"] for row in trade.data),
                    "long": sum(row["commission"] for row in long_trade.data),
                    "short": sum(row["commission"] for row in short_trade.data)
                    }
        except Exception as e:
            return e 
    
    async def largest_win_trade(self, acc_id:int, time="*"):
        try:
            if time == "*":
                trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).gt("profit_loss", 0).or_("trade_type.eq.sell, trade_type.eq.buy").order("profit_loss", desc=True).limit(1).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "buy").gt("profit_loss", 0).order("profit_loss", desc=True).limit(1).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "sell").gt("profit_loss", 0).order("profit_loss", desc=True).limit(1).execute()
           
                return {
                    "total": trade.data[0].get("profit_loss", 0) if trade.data else 0,
                    "long": long_trade.data[0].get("profit_loss", 0) if long_trade.data else 0,
                    "short": short_trade.data[0].get("profit_loss", 0) if short_trade.data else 0,
                    }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).gt("profit_loss", 0).gte("entry_time",past_date).or_("trade_type.eq.sell, trade_type.eq.buy").order("profit_loss", desc=True).limit(1).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "buy").gt("profit_loss", 0).gte("entry_time",past_date).order("profit_loss", desc=True).limit(1).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "sell").gt("profit_loss", 0).gte("entry_time",past_date).order("profit_loss", desc=True).limit(1).execute()
                
                return {
                    "total": trade.data[0].get("profit_loss", 0) if trade.data else 0,
                    "long": long_trade.data[0].get("profit_loss", 0) if long_trade.data else 0,
                    "short": short_trade.data[0].get("profit_loss", 0) if short_trade.data else 0,
                    }
        
        except Exception as e:
            return e    
        
    async def largest_loss_trade(self, acc_id:int, time="*"):
        try:
            if time == "*":
                trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).lt("profit_loss", 0).order("profit_loss", desc=True).limit(1).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "buy").lt("profit_loss", 0).order("profit_loss", desc=True).limit(1).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "sell").lt("profit_loss", 0).order("profit_loss", desc=True).limit(1).execute()
                
                return {
                    "total": trade.data[0].get("profit_loss", 0) if trade.data else 0,
                    "long": long_trade.data[0].get("profit_loss", 0) if long_trade.data else 0,
                    "short": short_trade.data[0].get("profit_loss", 0) if short_trade.data else 0,
                    }
            else:
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).lt("profit_loss", 0).gte("entry_time",past_date).order("profit_loss", desc=True).limit(1).execute()
                long_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "buy").lt("profit_loss", 0).gte("entry_time",past_date).order("profit_loss", desc=True).limit(1).execute()
                short_trade = self.supabase.table("trade_history").select("profit_loss").eq("account_id",acc_id).eq("trade_type", "sell").lt("profit_loss", 0).gte("entry_time",past_date).order("profit_loss", desc=True).limit(1).execute()
                
                return {
                    "total": trade.data[0].get("profit_loss", 0) if trade.data else 0,
                    "long": long_trade.data[0].get("profit_loss", 0) if long_trade.data else 0,
                    "short": short_trade.data[0].get("profit_loss", 0) if short_trade.data else 0,
                    }
        
        except Exception as e:
            return e    
    
    async def total_pips(self, acc_id:int, time="*"):
        try:
            if time =="*":
                # trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).execute()
                long_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "sell").execute()
                
                total_pips= 0
                total_long_pips = 0
                total_short_pips= 0
                
                for pip in long_trade.data:
                    sub = pip["exit_price"] - pip["entry_price"]
                    total_long_pips = sub + total_long_pips
                    
                for pip in short_trade.data:
                    sub = pip["entry_price"] - pip["exit_price"]
                    total_short_pips = sub + total_short_pips
                    
                total_pips = total_long_pips + total_short_pips
                
                return {
                    "total": total_pips,
                    "long": total_long_pips,
                    "short":total_short_pips
                    }
            else: 
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
                
                long_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "sell").gte("entry_time",past_date).execute()
                
                total_pips= 0
                total_long_pips = 0
                total_short_pips= 0
                
                for pip in long_trade.data:
                    sub = pip["exit_price"] - pip["entry_price"]
                    total_long_pips = sub + total_long_pips
                    
                for pip in short_trade.data:
                    sub = pip["entry_price"] - pip["exit_price"]
                    total_short_pips = sub + total_short_pips
                    
                total_pips = total_long_pips + total_short_pips
                
                return {
                    "total": total_pips,
                    "long": total_long_pips,
                    "short":total_short_pips
                    }
        except Exception as e:
            return e
        
    async def avg_pips(self, acc_id:int, time="*"):
        try:
            if time =="*":
                # trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).execute()
                long_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "buy").execute()
                short_trade = self.supabase.table("trade_history").select("entry_price","exit_price").eq("account_id",acc_id).eq("trade_type", "buy").execute()
                
                total_pips= 0
                total_long_pips = 0
                total_short_pips= 0
                
                for pip in long_trade.data:
                    sub = pip["exit_price"] - pip["entry_price"]
                    total_long_pips += sub 
                    
                for pip in short_trade.data:
                    sub = pip["entry_price"] - pip["exit_price"]
                    total_short_pips  += sub
                    
                total_pips = total_long_pips + total_short_pips
                
                long_count = len(long_trade.data)
                short_count = len(short_trade.data)
                total_count = long_count + short_count
                
                total_avg_pip = total_pips/ total_count if total_count > 0 else 0
                long_avg_pip = total_long_pips/long_count if long_count > 0 else 0
                short_avg_pip = total_short_pips/short_count if short_count > 0 else 0
                return {
                    "total": total_avg_pip,
                    "long": long_avg_pip,
                    "short":short_avg_pip
                    }
            else: 
                period_in_days = time_period[time]
                past_date = get_past_date(period_in_days)
             
                
                long_trade = self.supabase.table("trade_history").select("entry_price","exit_price",count="exact").eq("account_id",acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                short_trade = self.supabase.table("trade_history").select("entry_price","exit_price",count="exact").eq("account_id",acc_id).eq("trade_type", "buy").gte("entry_time",past_date).execute()
                
                total_pips= 0
                total_long_pips = 0
                total_short_pips= 0
                
                for pip in long_trade.data:
                    sub = pip["exit_price"] - pip["entry_price"]
                    total_long_pips = sub + total_long_pips
                    
                for pip in short_trade.data:
                    sub = pip["entry_price"] - pip["exit_price"]
                    total_short_pips = sub + total_long_pips
                    
                
                total_pips = total_long_pips + total_short_pips
                long_count = (long_trade.count)
                short_count = (short_trade.count)
                total_count = long_count + short_count
                
                total_avg_pip = total_pips/ total_count if total_count > 0 else 0
                long_avg_pip = total_long_pips/long_count if long_count > 0 else 0
                short_avg_pip = total_short_pips/short_count if short_count > 0 else 0
                return {
                    "total": total_avg_pip,
                    "long": long_avg_pip,
                    "short":short_avg_pip
                    }
        except Exception as e:
            return e
        
    
    
    async def acct_perf(self, acc_id:int, time="*"): 
        try:
            net_profit = await self.net_profit(acc_id,time)
            percent_return = await self.percent_total_return(acc_id,time)
            avg_trade = await self.avg_return_per_trade(acc_id,time)
            percent_win_trade = await self.percent_winning_trade(acc_id,time)
            percent_loss_trade = await self.percent_losing_trade(acc_id, time)
            profit_factor = await self.cal_profit_factor(acc_id, time)
            avg_trade_dur = await self.avg_loss_trade_duration(acc_id, time)
            avg_loss_trade = await self.avg_loss_trade_duration(acc_id, time)
            avg_win_trade = await self.avg_win_trade_duration(acc_id,time)
            total_trades = await self.get_total_trades(acc_id,time)
            win_trades = await self.get_total_win_trades(acc_id, time)
            loss_trades = await self.get_total_loss_trades(acc_id,time)
            traded_lot = await self.traded_lot(acc_id,time)
            commission = await self.total_commission(acc_id, time)
            largest_win_trade = await self.largest_win_trade(acc_id, time)
            largest_loss_trade = await self.largest_loss_trade(acc_id,time)
            total_pips = await self.total_pips(acc_id, time)
            avg_pips = await self.avg_pips(acc_id, time)
            
            perfomance = {
                "period": time,
                "Net profit":net_profit,
                # "Profit factor":profit_factor,
                "Commission": commission,
                "Total trades": total_trades,
                "Average trade duration":  avg_trade_dur,
                "Percentage return": percent_return,
                "Winning trades":win_trades,
                "Largest winning trades":largest_win_trade,
                # "Percent winning trades": percent_win_trade,
                "Average win trade duration": avg_win_trade,
                "Losing trades":loss_trades,
                "Largest losing trades":largest_loss_trade,
                # "Percent winning trades": percent_loss_trade,
                "Average loss trades duration":avg_loss_trade,
                "Average trade": avg_trade,
                "Total pips": total_pips,
                "Average pips":avg_pips,
                "Total lot": traded_lot,
                
            }
            
            return perfomance
        except Exception as e:
            return e
    
    async def store_stat(self, acc_id:int, stats:dict):
        # Check if the account id and period exist if exist the update
        # add for new accounts
        
        # For loop 
        stat_arr = []
        new_arr = []
        # print(stats)
        for period in stats:
            # print(json.dumps(stats[period]))
            # print(acc_id)
            acc_period = self.supabase.table("performance").select("*",count="exact").eq("account_id",acc_id).eq("period",period).execute()
            print(acc_period.count)
            
            
            if acc_period.count > 0:
                # self.supabase.table("Performance").update
                perf_data = {
                    "id": acc_period.data[0]["id"]    ,
                    "account_id": acc_id,
                    "period": period,
                    "performance": json.dumps(stats[period]),
                    "updated_at": datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")
                }
                
                stat_arr.append(perf_data)
                
                
            else:
                perf_data = {
               
                    "account_id": acc_id,
                    "period": period,
                    "performance":json.dumps(stats[period]),
                    "updated_at": datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")
                }
                
                new_arr.append(perf_data)
        
        
        
                # self.supabase.table("Performance").insert(per)
        if  stat_arr:
            
            self.supabase.table("performance").upsert(stat_arr).execute()
            
            
        if new_arr:
            
            self.supabase.table("performance").insert(new_arr).execute()
            
        
    #Implement Max drawdown
    # async def roi(self, acc_id:int):
    #     pass
    
    # async def current_exposure(self, acc_id:int):
    #     pass
    
    # async def percentage_max_drawdown(self, acc_id:int):
    #     pass
    
    # async def monthly_return(self, acc_id:int):
    #     pass
    
    # async def total_return(self, acc_id:int):
    #     pass
    
    # async def projected_year_return(self, acc_id:int):
    #     pass