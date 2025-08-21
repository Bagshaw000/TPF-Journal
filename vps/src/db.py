import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

def supabase_conn() -> Client:        
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set as environment variables.")
    supabase_client: Client = create_client(url, key)
    
    return supabase_client


if __name__ == '__main__':
    asyncio.run(supabase_conn())                 

        
