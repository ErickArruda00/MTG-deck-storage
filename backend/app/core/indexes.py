from app.core.db import db


async def create_indexes():
    await db.cards.create_index("scryfall_id", unique=True)
    await db.cards.create_index("name")
    await db.cards.create_index("colors")
    await db.cards.create_index("rarity")
    await db.cards.create_index("type_line")
    
    await db.decks.create_index("name", unique=True)
    await db.decks.create_index("format")
    await db.decks.create_index("created_at")

