from src.model import User, Session, ReturnType
from supabase import create_client, Client
from .db import supabase_conn
from src.utils import encrypt,decrypt
from datetime import datetime
from dotenv import load_dotenv

import json

load_dotenv()

class Auth:
   
    def __init__(self):
        
        self.supabase = supabase_conn()
       
        
       
    '''
    The class handles user signup and authentication
    '''    
    async def create_user(self,data:User)->ReturnType:
        try:
            # Authenticate the user
            
            response = self.supabase.auth.sign_up(
                    {
                    "email": data.email,
                    "password": data.password,
                }
            )
            
            # Get the user id after signup
            
            usr_id = self.supabase.auth.get_user().user
            
        
            # If no error the connect to db and store the user details   
            if response:
                
                usr_data = {
                        "id": usr_id.id,
                        "first_name": encrypt(data.first_name),
                        "email": encrypt(data.email) ,
                        "last_name": encrypt(data.last_name),
                        "plan": 'free',
                        "password": encrypt(data.password),
                        "country": data.country,
                         "last_update": datetime.now().astimezone().strftime("%Y/%m/%d, %H:%M:%S")
                    }
                
                usr = self.supabase.table("user").insert(usr_data).execute()
            
            
                #Checking if the data was returned successfully or not
                if usr:
                
                    return {
                        "data":usr,
                        "msg": "Successfully added user data",
                        "status": 200
                    }
              
                return {
                    "msg":"Failed to add user",
                    "status": 500
                }

        except Exception as e:
            
            return e

    '''
        This class gets the user by id
    '''
    async def get_user_by_id(self,id:str)->ReturnType:
        try:
          
            #Check for user base on the id
            user_obj = self.supabase.table('user').select("id").eq(id).execute()
            
            #Disconnect database
           
            #Check if the any data was returned or not
            if user_obj:
                return {
                    "status":500,
                    "msg": "User already exist",
                    "data": user_obj
                }
            
            return {
                "status":200,
                "msg": "No user",
            }
            
            
        except Exception as e:
            return e
            
         
        
