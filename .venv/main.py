from typing import Union
import asyncio
from fastapi import FastAPI
from src.db import main
from dotenv import load_dotenv
from prisma.models import  user
from src.metatrader import MetaTrader
import MetaTrader5 as mt5
from src.model import User
from src.auth import Auth
import os
from supabase import create_client, Client

load_dotenv()


app = FastAPI()
# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase_client: Client = create_client(url, key)
auth_class = Auth()


@app.on_event("startup")
async def on_startup():
    pass
    # db = await main()
    # db_conn = await db.connect()
    
    # if db_conn:
    #     print("Successfull connection")
    # else:
    #     print("Connection not successful")
        
    # await db.disconnect()
    
    # if not mt5.initialize():
    #     print("Initiliazed failed, error code",mt5.last_error())
        
    # else:
    #     print(mt5.terminal_info())
        
    

@app.get("/")
async def read_root():
    #await dbConn()
    # print("Test")
    # await dbConn()
    public_key = os.environ.get("RSA_PUBLIC_KEY")
    print(public_key)
    return {"Hello": "World"} 

@app.post('/signup')
async def create_user(req:User):
    # print(req)
    user = await auth_class.create_user(req)
    
    return user


    
    # print(req)
    
    # response = supabase.auth.sign_up(
    # {
    #     "email": req.email,
    #     "password": req.password,
    # })
    # db = await main()
    # await db.connect()
    # usr = await user.prisma().create(
    #     data={
    #         'first_name': req.first_name,
    #         'email': req.email,
    #         'last_name': req.last_name,
    #         'plan': 'free',
    #         'password': req.password
    #     },
    # )
    # if response & usr:
    #     return response
    # else:
    

    
    
    #     return {" status":"error"}
    
    # mt5.login(52443177,password="ZQ$$KV$Pp9lMYz",server="ICMarketsSC-Demo")
    # mt5.shutdown()
    
    