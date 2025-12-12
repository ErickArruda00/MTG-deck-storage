from fastapi import APIRouter
from app.core.db import db

router = APIRouter()

@router.get("/test")
async def test_mongo():
    count = await db.cards.count_documents({})
    return {"mongo_status": "ok", "total_cards": count}