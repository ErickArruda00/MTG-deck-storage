from fastapi import APIRouter
from app.core.db import db

router = APIRouter()

@router.get("/test")
async def test_decks():
    """Endpoint de teste para verificar conexão com coleção de decks"""
    count = await db.decks.count_documents({})
    return {"mongo_status": "ok", "total_decks": count}

