import MetaTrader5 as mt5

class MetaTrader:
    def __init__(self ):
        if not mt5.initialize():
            print("Initiliazed failed, error code",mt5.last_error())
        print(mt5.terminal_info())
        
    def login(login:int, server:str, password:str):
        try:
            mt5.login(login, server, password)
            mt5.shutdown()
        except:
            print("Error login")