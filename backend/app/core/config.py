import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB", "mtg_database")
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

API_PORT = int(os.getenv("API_PORT", "8000"))

SCRYFALL_API_URL = "https://api.scryfall.com"

if not MONGO_USER or not MONGO_PASS:
    raise ValueError(
        "Variáveis de ambiente MONGO_USER e MONGO_PASS devem estar definidas no arquivo .env"
    )

