from rsa_crypto_manager import RSACryptoManager
import os

crypto =  RSACryptoManager()

private_key:str = os.environ.get("RSA_PRIVATE_KEY")
public_key:str = os.environ.get("RSA_PUBLIC_KEY")

def encrypt(data:str|int):
    encrypted_data = crypto.encrypt(data, public_key)
    return encrypted_data

def decrypt(data):
    encrypted_data = crypto.decrypt(data, public_key)
    return encrypted_data