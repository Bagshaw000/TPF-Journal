import os
from cryptography.fernet import Fernet
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

