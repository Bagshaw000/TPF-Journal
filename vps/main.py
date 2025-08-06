from typing import Union
import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from src.db import main
import MetaTrader5 as mt5
from src.model import Mt5_Model
from src.mt5 import Mt5_Action



app = FastAPI()
mt5_obj = Mt5_Action()


@app.on_event("startup")
async def on_startup():  
    
    if not mt5.initialize():
        print("Initiliazed failed, error code",mt5.last_error())
        
    else:
        print(mt5.terminal_info()._asdict())
        
    

@app.get("/")
async def read_root():
    #await dbConn()
    # print("Test")
    # await dbConn()
    return {"Hello": "World"} 

@app.get('/setup')
async def get_user(req:Mt5_Model):    
    #     return {" status":"error"}
    print(req)
    return await mt5_obj.setup_Account(req)
    
    
    