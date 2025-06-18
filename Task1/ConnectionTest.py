from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()
env_connection_string = os.getenv('connection_string')

try:
    client = MongoClient(env_connection_string, serverSelectionTimeoutMS=3000)

    client.admin.command("ping")
    print("Connection successful!")

except ConnectionFailure as e:
    print("Connection failed!")
    print(f"Reason: {e}")
