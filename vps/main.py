from typing import Union
import asyncio
from fastapi import FastAPI, WebSocketDisconnect, APIRouter
import os
import MetaTrader5 as mt5
from src.model import Acc_Model,Deal_Req,Pos_Id, Acc_Id,User,Return_Type
from fastapi.encoders import jsonable_encoder
from src.mt5 import Mt5_Class
from src.auth import Auth
from src.account import Accounts
from src.position import Position
from src.performance import Performance
import json
from datetime import datetime
import websockets
from websockets.sync.client import connect
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(init_mt5())
    # Start background tasks AFTER FastAPI is up
    asyncio.create_task(mt5_producer())
    # Run the producer in the background as a concurrent task
    asyncio.create_task(producer())
    
    #Assign three three consumers to handle the task in the queue
    for _ in range(3):
        asyncio.create_task(consumer())
        
    # for _ in range(3):
    #     asyncio.create_task(funding_consumer())
    
    for _ in range(3):
        asyncio.create_task(perform_consumer())  
        
    for _ in range(3):
        asyncio.create_task(mt5_consumer())
        
    yield


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api/v1")
mt5_obj = Mt5_Class()
auth_obj = Auth()
acc_obj = Accounts()
pos_obj = Position()
perf_obj = Performance()
queue = asyncio.Queue(maxsize=100)
perf_queue = asyncio.Queue(maxsize=100)
mt5_acc_queue = asyncio.Queue(maxsize=100)
funding_info = asyncio.Queue(maxsize=100)


async def producer():
    try:
        while True:
            acc_list = await acc_obj.get_all_account()
            if acc_list:
                
                
                for acc in acc_list:
                   
                    # print(acc_list)
                    await queue.put(acc)
                    await perf_queue.put(acc)
                    fund_det =  Deal_Req(login=int(acc["account_no"]), password=str(acc["password"]),server=str(acc['server_name']),platform='mt5',from_=datetime(2015,1,1))
                    await mt5_obj.get_funding_details(fund_det,acc["id"])
                   
                    # await funding_info.put(fund_detail)
                    # print(fund_detail)
                    asyncio.create_task(mt5_obj.get_funding_details(fund_det, acc["id"]))
                    
                    
            await asyncio.sleep(20)
    except Exception:
        await asyncio.sleep(3)
        


async def init_mt5():
    while not mt5.initialize():
        print("MT5 init failed, retrying...")
        await asyncio.sleep(5)

          
'''
This consumes the information stored in the queue and broadcast the 
open position 
'''
async def consumer():

    try:

        while True:
            user = await queue.get()

            # print(user["id"])
            # print(user["platform"])
           
            
            # print(acc)
            if user["platform"] == "mt5":
                acc_det =Acc_Model(login=int(user["account_no"]), password=str(user["password"]),server=str(user['server_name']),platform='mt5')
                
                user_position = await mt5_obj.get_open_position(acc_det)
                # print(user_position)
                
                if user_position == None:
                    print("No position returned")
                    continue
                else:
                    # This does not allow update of the last open position so do the check in the store open position
                    await pos_obj.new_store_mt5_open_pos(user_position)     
                 
            
            queue.task_done()
    except Exception as e:
        print("Live trade Consumer is disconnected")
        await asyncio.sleep(5)
        # await consumer()



async def perform_consumer():
    try:
        while True:
            user = await perf_queue.get()
        
            
            if user:
                # print(user)
             
                all_history = await perf_obj.acct_perf(user["id"],"*")
                yes_history = await perf_obj.acct_perf(user["id"],"y")
                tw_history = await perf_obj.acct_perf(user["id"],"t-w")
                lw_history = await perf_obj.acct_perf(user["id"],"l-w")
                tm_history = await perf_obj.acct_perf(user["id"],"t-m")
                lm_history = await perf_obj.acct_perf(user["id"],"l-m")
                m3_history = await perf_obj.acct_perf(user["id"],"3-m")
                m6_history = await perf_obj.acct_perf(user["id"],"6-m")
                m12_history = await perf_obj.acct_perf(user["id"],"12-m")
                
                dict_history:dict = {
                    "*":all_history,
                    "y":yes_history,
                    "t-w":tw_history,
                    "l-w":lw_history,
                    "t-m":tm_history,
                    "l-m":lm_history,
                    "3-m":m3_history,
                    "6-m":m6_history,
                    "12-m":m12_history
                    }

                # print(lw_history)
                # print(yes_history)
                # print(tw_history)
                # print(lm_history)
                # print(m3_history)
                # print(m6_history)
                # print(m12_history)
                store_all = await perf_obj.store_stat(user["id"], dict_history)
                
                print(store_all)
            perf_queue.task_done()
    except Exception as e:
        print(e)
        await asyncio.sleep(30)
        # await perform_consumer()
        
'''
This producer  get all the user account and adds them to the queue every 12 hours you can combine the producer of the open position
'''
async def mt5_producer():
    while True:
        try:
            mt5_accounts = await acc_obj.get_all_mt5_account()
            # print(mt5_accounts)
            for acc in mt5_accounts:
                # print(acc)
                await mt5_acc_queue.put(acc)
            await asyncio.sleep(10)
        except Exception as e:
            await asyncio.sleep(30)
            
            
       

'''
Passes the account form the queue to update account to checking if trade has occurred with that the last entry in the database
'''
async def mt5_consumer():
    while True:
        acc = await mt5_acc_queue.get()
        
        try:
            print("Error")
            
            await pos_obj.get_all_user_last_trade(acc)
           
        except Exception as e:
            print(f"Error processing account {acc['id']}: {e}")
            await asyncio.sleep(3)
        finally:
            mt5_acc_queue.task_done()
            
            
async def funding_consumer():
    url:str= os.environ.get("FUNDING_WEBSOCKET")
    
    # make the connection persistent
    

        
        #Broad cast the information to the websocket
    try:
        async with websockets.connect(url) as socket_conn:
                    # Get the queue with login credential 
            while True:
                fund_info = await funding_info.get()
                
                #For each mt5 account get the open positions
                # user_position = await mt5_obj.get_open_position(user)
                # print(user_position)
                await socket_conn.send(json.dumps(jsonable_encoder(fund_info)))
                 
                funding_info.task_done()
    except WebSocketDisconnect:
        print("Websocket disconnected")
        await asyncio.sleep(24 * 60 * 60)
        
    

@app.on_event("startup")
async def on_startup(): 
    pass
    # Initialize the Mt5 console on startup  
    # if not mt5.initialize():
    #     print("Initiliazed failed, error code",mt5.last_error())
    #     #(Send a request that mt5server down)
        

        
        
    

@app.get("/")
async def read_root():

    return {"Hello": "World"} 




'''
Authentication Routes
'''

# Authentication route
@router.post('/auth/signup', tags=['auth'])
async def create_user(req:User, res:Return_Type):
    user = await auth_obj.create_user(req)
    
    if user:
        res =Return_Type(status=True,msg="Success",data=None)
        return res
    
    return Return_Type(status=False, msg="Failed", data=None)

@router.post('/account/setup/{user_id}', tags=["account"])
async def setup_account(user_id:str,req:Deal_Req,starting_bal:float):
    
    print(user_id)
    print(req)
    res = await acc_obj.account_setup(user_id, req, starting_bal)

    
    return res


@router.post('/mt5/setup',)
async def get_user(req:Deal_Req):    
    #     return {" status":"error"}
    print(req)
    req_data:Acc_Model = req
    acc_data = await mt5_obj.setup_Account(req_data)
    
    return acc_data


# Test the login
# @app.post("/account_info")
# async def get_acc_info(req:Acc_Model):
#     acc_detail = await mt5_obj.get_account_details(req)
#     return acc_detail
    
# @app.post("/funding_details")
# async def get_acc_funding(req:Deal_Req):
#     print(req.from_)
#     fund_details = await mt5_obj.get_funding_details(req)
#     return fund_details

# @app.post("/open_position")
# async def get_open_position(req:Acc_Model):
#     open_position = await mt5_obj.get_open_position(req)
#     return open_position

# @app.post("/deal")
# async def get_deal(req:Deal_Req):
#     to_ = datetime.now()
#     print(req)
#     deal_data = await mt5_obj.get_deal_history(req.from_,to_,req)
#     return deal_data

# @app.post("/deal/pos_id")
# async def get_deal_by_pos_id(req:Pos_Id):
#     print(req)
#     deal_data = await mt5_obj.get_deal_by_pos_id(req.pos_id)
#     return deal_data

# @app.post("/order/pos_id")
# async def get_order_by_pos_id(req:Pos_Id):
#     print(req.pos_id)
#     deal_data = await mt5_obj.get_order_by_pos_id(req.pos_id)
#     return deal_data


# @app.post('/last_trade')
# async def get_last_trade(req:Acc_Id):
#     trade= await acc_obj.get_user_last_trade(req.acc_id)
    
#     return trade

# @app.post('/all_trade')
# async def get_last_trade():
#     trade= await acc_obj.get_all_user_last_trade()
    
#     return trade


app.include_router(router)