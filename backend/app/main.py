from fastapi import FastAPI
from app.db import db

app = FastAPI()

@app.get("/")
async def root():
    count = await db["test"].count_documents({})
    return {"msg": "API funcionando!", "docs_no_banco": count}
