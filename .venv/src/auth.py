from src.model import User, Session, ReturnType
from supabase import create_client, Client
import os
# from src.db import main
from .db import supabase_conn,main
from src.utils import encrypt,decrypt
from datetime import datetime
from dotenv import load_dotenv
from prisma.models import  user
import json

load_dotenv()

class Auth:
   
    def __init__(self):
        # url: str = os.environ.get("SUPABASE_URL")
        # key: str = os.environ.get("SUPABASE_KEY")
        # supabase: Client = create_client(url, key)
        self.supabase = supabase_conn()
        pass
        
       
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
            
            # Parse the Authentication data to json to get the user id
            test = json.loads(response.model_dump_json())
            
            user_id : str = test["user"]["id"]
            
            
            # If no error the connect to db and store the user details   
            if response:
                
                #Database connection
                db = await main()
                await db.connect()
                
                #Add user data to the database and encrypt sensitive data
                usr = await user.prisma().create(
                data={
                    'id': user_id,
                    'first_name': encrypt(data.first_name),
                    'email': encrypt(data.email) ,
                    'last_name': encrypt(data.last_name),
                    'plan': 'free',
                    'password': encrypt(data.password),
                    'country': data.country,
                    'last_update': datetime.now()
                    },
                )
                
                #Disconnect the database 
                await db.disconnect()
                
                #Checking if the data was returned successfully or not
                if usr:
                
                    return {
                        "data":usr.model_dump_json(),
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
            #Instantiate a database connection
            db = await main()
            await db.connect()
            
            #Check for user base on the id
            user_obj = await db.user.find_first(where={
                'id' : id,
            }) 
            
            #Disconnect database
            await db.disconnect()
            
            #Check if the any data was returned or not
            if user_obj != None:
                return {
                    "status":500,
                    "msg": "User already exist",
                    "data": user_obj.model_dump_json()
                }
            
            return {
                "status":200,
                "msg": "No user",
            }
            
            
        except Exception as e:
            return e
            
         
        
