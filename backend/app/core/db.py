"""
Conexão com o banco de dados MongoDB
"""
import motor.motor_asyncio
from app.core.config import MONGO_USER, MONGO_PASS, MONGO_DB, MONGO_HOST, MONGO_PORT

# Construir URL de conexão
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

# Criar cliente MongoDB assíncrono
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Acessar o banco de dados
db = client[MONGO_DB]
