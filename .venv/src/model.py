from pydantic import BaseModel

class User(BaseModel):
    first_name:str
    last_name:str
    country: str
    last_update:str | None = None
    plan: str | None = None
    email: str | None = None
    password: str 
    
class Session(BaseModel):
    access_token:str
    refresh_token:str
    expires_in:int
    expires_at: int
    token_type:str
    
class DataType(BaseModel):
    status: int
    msg: str | None
    data: object | str | None