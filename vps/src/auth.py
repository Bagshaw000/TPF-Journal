from src.model import User
from supabase import create_client, Client
from .db import supabase_conn
from src.utils import encrypt,decrypt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Auth:
    
    def __init__(self):
        
        self.supabase = supabase_conn()
        
        
    '''
    The class handles user signup and authentication
    '''    
    async def create_user(self,data:User):
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
              
                return usr

        except Exception as e:
            
            return e

    '''
        This class gets the user by id
    '''
    async def get_user_by_id(self,id:str):
        try:
          
            #Check for user base on the id
            user_obj = self.supabase.table('user').select("*").eq('id',id).execute()
            
            #Disconnect database
           
            #Check if the any data was returned or not
        
            return user_obj
            
            
        except Exception as e:
            return e
    
     
    '''
        This class gets the user by email
    '''   
    async def get_user_by_email(self, email:str):
        try:
            user_obj = self.supabase.table('user').select("*").eq('email',email).execute()
            
            return user_obj
        except Exception as e:
            return e
     
            
    '''
        This class edits the user details
    '''
    async def edit_user_details(self,id:str, data):
        try:
            user = self.supabase.table('user').update(data).eq('id',id).execute()

            return user
        except Exception as e:
            return e  
    
    '''
    The password reset will happen on the frontend
    '''
    
        
