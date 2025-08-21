import asyncio
from fastapi import FastAPI, Response, status,WebSocket,WebSocketDisconnect
from dotenv import load_dotenv
from src.models import User, Acc_Model, AccId
from src.auth import Auth
from src.accounts import MT5_Class
from src.position import Position
from src.trade_history import Trader_History
import os
from fastapi.encoders import jsonable_encoder

from datetime import datetime

load_dotenv()


app = FastAPI()
auth_class = Auth()
mt5_class = MT5_Class()
trade_hist = Trader_History()
position = Position()
live_mt5_queue = asyncio.Queue()
mt5_last_queue = asyncio.Queue()




@app.on_event("startup")
async def on_startup():
    asyncio.create_task(live_mt5_consumer())
   
        

        
    

@app.get("/")
async def read_root():
    #await dbConn()
    # print("Test")
    # await dbConn()
    
    
    return {"Hello": "World"} 

'''
Endpoint to signup the user
'''
@app.post('/signup')
async def create_user(req:User, res:Response):

    user = await auth_class.create_user(req)
    
    if user:
        res.status_code = status.HTTP_201_CREATED
        return user
    
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return user


'''
This endpoint setup the user trading account by importing the trade history
''' 
@app.get('/setup/{user_id}')
async def setup_trading_account(user_id:str,req:Acc_Model, res:Response):
   
    data = await mt5_class.account_setup(user_id=user_id,acc=req)
    
    if data:
        print(data)
        res.status_code = status.HTTP_201_CREATED
        return data
    
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return data

'''
Websocket to receive trade update from the mt5 server
'''
@app.websocket("/livetrade")
async def mt5_live_trade(websocket:WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await live_mt5_queue.put(data)

                
            # await position.store_mt5_open_pos(data)
          
    except WebSocketDisconnect:
        print('errorr')
    
    
async def live_mt5_consumer():
    while True:
        mt5_trade = await live_mt5_queue.get()
        print(mt5_trade)
        store_pos  = await position.store_mt5_open_pos(mt5_trade)
        await asyncio.sleep(10)
        live_mt5_queue.task_done()


