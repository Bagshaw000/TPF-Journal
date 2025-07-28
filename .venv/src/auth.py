from src.model import User, Session
from supabase import create_client, Client
import os
from db import main
from utils import encrypt,decrypt
from datetime import datetime

class Auth:
    
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
       
        
    async def create_user(self,user:User):
        try:
            db = await main()
            response = self.supabase.auth.sign_up(
                    {
                    "email": user.email,
                    "password": user.password,
                }
            )
            
            if response:
                await db.connect()
                
                usr = await user.prisma().create(
                data={
                    'first_name': encrypt(user.first_name),
                    'email': encrypt(user.email) ,
                    'last_name': encrypt(user.last_name),
                    'plan': 'free',
                    'password': encrypt(user.password),
                    'country': user.country,
                    'last_update': datetime.now()
                    },
                )
                
                await db.disconnect()
                
                if usr:
                    ses_data : Session = response.session
                    return {
                        "data":ses_data,
                        "msg": "Successfully added user data",
                        "status": 200
                    }
                else:
                    return {
                        "msg":"Failed to add user",
                        "status": 500
                    }
                    
            else:
                return{
                    "status": 500,
                    "msg":"Failed to authenticate user"
                }
                
                
                
            
        except :
            return {
                "status": 500,
                "msg":"An exception was thrown",
                
            }
        