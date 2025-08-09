from fastapi import FastAPI, Response, status
from dotenv import load_dotenv
from src.model import User, Acc_Model
from src.auth import Auth
from src.metatrader import MT5_Class
import os
from fastapi.encoders import jsonable_encoder

from datetime import datetime

load_dotenv()


app = FastAPI()
# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase_client: Client = create_client(url, key)
auth_class = Auth()
mt5_class = MT5_Class()

@app.on_event("startup")
async def on_startup():
    pass

        
    

@app.get("/")
async def read_root():
    #await dbConn()
    # print("Test")
    # await dbConn()
    
    public_key = os.environ.get("RSA_PUBLIC_KEY")
    print(public_key)
    return {"Hello": "World"} 

@app.post('/signup')
async def create_user(req:User, res:Response):

    user = await auth_class.create_user(req)
    
    if user.status == 200:
        res.status_code = status.HTTP_201_CREATED
        return user
    
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return user


    
@app.get('/setup/{user_id}')
async def setup_trading_account(user_id:str,req:Acc_Model, res:Response):
   
    data = await mt5_class.account_setup(user_id=user_id,acc=req)
    
    if data:
        print(data)
        res.status_code = status.HTTP_201_CREATED
        return data
    
    res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return data

    


