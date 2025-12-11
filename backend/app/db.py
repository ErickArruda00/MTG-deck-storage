import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_USER or not MONGO_PASS or not MONGO_DB:
    raise ValueError("Variáveis de ambiente MONGO_USER, MONGO_PASS e MONGO_DB devem estar definidas no arquivo .env")

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@mongo:27017/"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
