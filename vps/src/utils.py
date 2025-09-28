import os
from cryptography.fernet import Fernet
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
load_dotenv()


key = str(os.environ.get("FERNET_KEY"))
key_byte = key.encode("utf-8")
crypto = Fernet(key= key_byte)


# This encrypt the data 
def encrypt(data):
    encrypted_data = crypto.encrypt(data.encode("utf-8"))

    return encrypted_data.decode("utf-8")

# This dencrypt the data
def decrypt(data):
    decrypted_data = crypto.decrypt(data.encode("utf-8"))

    return decrypted_data.decode("utf-8")

def get_past_date(days_sub, from_date: date | None = None)-> date:
    if from_date is None:
        from_date = datetime.now()
    return from_date - timedelta(days=days_sub)