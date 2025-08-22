from typing import Union
import asyncio
from fastapi import FastAPI, WebSocketDisconnect
import os
import MetaTrader5 as mt5
from src.model import Mt5_Model,DealReq,PosId, AccId
from fastapi.encoders import jsonable_encoder
from src.mt5 import Mt5_Action
from src.account import Accounts
import json
from datetime import datetime
import websockets
from websockets.sync.client import connect
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
mt5_obj = Mt5_Action()
acc_obj = Accounts()
queue = asyncio.Queue()
mt5_acc_queue = asyncio.Queue()
funding_info = asyncio.Queue()


async def producer():
    while True:
        acc_list = await acc_obj.get_all_mt5_account()
        if acc_list:
        
            for acc in acc_list:
            
            
                login_det = Mt5_Model(login=int(acc["account_no"]), password=str(acc["password"]),server=str(acc['server_name']),platform='mt5')
                fund_det =  DealReq(login=int(acc["account_no"]), password=str(acc["password"]),server=str(acc['server_name']),platform='mt5',from_=datetime(2015,1,1))
                fund_detail = await acc_obj.get_funding_details(fund_det)
                
                await funding_info.put(fund_detail)
                await queue.put(login_det)
                
                
       
        await asyncio.sleep(10)
            
'''
This consumes the information stored in the queue and broadcast the 
open position to the websocket
'''
async def consumer():
    # Get the websocket url
    url:str= os.environ.get("WEBSOCKET")
    
    # make the connection persistent
    

        
        #Broad cast the information to the websocket
    try:
        async with websockets.connect(url) as socket_conn:
                    # Get the queue with login credential 
            while True:
                user = await queue.get()
                
                #For each mt5 account get the open positions
                user_position = await mt5_obj.get_open_position(user)
                print(user_position)
                await socket_conn.send(json.dumps(user_position))
                 
                queue.task_done()
    except WebSocketDisconnect:
        print("Websocket disconnected")
        await asyncio.sleep(3)
        consumer()
                 

'''
This producer  get all the user account and adds them to the queue every 12 hours
'''
async def mt5_producer():
    while True:
        mt5_accounts = await acc_obj.get_all_mt5_account()
        
        for acc in mt5_accounts:
            await mt5_acc_queue.put(acc)
        await asyncio.sleep(12 * 60 * 60)
       

'''
Passes the account form the queue to update account
'''
async def mt5_consumer():
    while True:
        acc = await mt5_acc_queue.get()
        
        try:
            await acc_obj.get_all_user_last_trade(acc)
           
        except Exception as e:
            print(f"Error processing account {acc['id']}: {e}")
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
        funding_consumer()
    

@app.on_event("startup")
async def on_startup():  
    asyncio.create_task(mt5_producer())
    # Run the producer in the background as a concurrent task
    asyncio.create_task(producer())
    
    #Assign three three consumers to handle the task in the queue
    for _ in range(3):
        asyncio.create_task(consumer())
        
    for _ in range(3):
        asyncio.create_task(funding_consumer())
        
        
    for _ in range(3):
        asyncio.create_task(mt5_consumer())
   
    # Initialize the Mt5 console on startup  
    if not mt5.initialize():
        print("Initiliazed failed, error code",mt5.last_error())
        #(Send a request that mt5server down)
        

        
        
    

@app.get("/")
async def read_root():

    return {"Hello": "World"} 

@app.post('/setup')
async def get_user(req:DealReq):    
    #     return {" status":"error"}
    print(req)
    req_data:Mt5_Model = req
    acc_data = await mt5_obj.setup_Account(req_data)
    
    return acc_data

@app.post("/account_info")
async def get_acc_info(req:Mt5_Model):
    acc_detail = await mt5_obj.get_account_details(req)
    return acc_detail
    
@app.post("/funding_details")
async def get_acc_funding(req:DealReq):
    print(req.from_)
    fund_details = await mt5_obj.get_funding_details(req)
    return fund_details

@app.post("/open_position")
async def get_open_position(req:Mt5_Model):
    open_position = await mt5_obj.get_open_position(req)
    return open_position

@app.post("/deal")
async def get_deal(req:DealReq):
    to_ = datetime.now()
    print(req)
    deal_data = await mt5_obj.get_deal_history(req.from_,to_,req)
    return deal_data

@app.post("/deal/pos_id")
async def get_deal_by_pos_id(req:PosId):
    print(req)
    deal_data = await mt5_obj.get_deal_by_pos_id(req.pos_id)
    return deal_data

@app.post("/order/pos_id")
async def get_order_by_pos_id(req:PosId):
    print(req.pos_id)
    deal_data = await mt5_obj.get_order_by_pos_id(req.pos_id)
    return deal_data


@app.post('/last_trade')
async def get_last_trade(req:AccId):
    trade= await acc_obj.get_user_last_trade(req.acc_id)
    
    return trade

# @app.post('/all_trade')
# async def get_last_trade():
#     trade= await acc_obj.get_all_user_last_trade()
    
#     return trade