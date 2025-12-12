from fastapi import FastAPI
from app.core.db import db
from app.routers import cards

app = FastAPI()

@app.get("/")
async def root():
    count = await db["test"].count_documents({})
    return {"msg": "API funcionando!", "docs_no_banco": count}

app.include_router(cards.router, prefix="/cards")