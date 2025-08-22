from .db import supabase_conn                                                                                                                                                                                                                                                                                                                                                                                             
class Performance:
    
    def __init__(self):
    
        self.supabase = supabase_conn()
