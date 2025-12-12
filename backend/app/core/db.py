import motor.motor_asyncio
from app.core.config import MONGO_USER, MONGO_PASS, MONGO_DB, MONGO_HOST, MONGO_PORT

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]
