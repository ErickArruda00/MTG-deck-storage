from fastapi import FastAPI
from app.core.db import db
from app.routers import cards, decks

app = FastAPI(
    title="MTG Deck Storage API",
    description="Sistema para gerenciar banco de cartas de Magic: The Gathering",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint raiz - informações da API"""
    cards_count = await db.cards.count_documents({})
    decks_count = await db.decks.count_documents({})
    return {
        "msg": "API funcionando!",
        "total_cards": cards_count,
        "total_decks": decks_count
    }

# Incluir routers
app.include_router(cards.router, prefix="/cards", tags=["cards"])
app.include_router(decks.router, prefix="/decks", tags=["decks"])