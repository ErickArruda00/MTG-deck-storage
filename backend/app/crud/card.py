from typing import Optional, Dict, Any, List
from app.core.db import db


async def get_card_by_scryfall_id(scryfall_id: str) -> Optional[Dict[str, Any]]:
    card = await db.cards.find_one({"scryfall_id": scryfall_id})
    return card


async def get_cards_by_scryfall_ids(scryfall_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    if not scryfall_ids:
        return {}
    
    cursor = db.cards.find({"scryfall_id": {"$in": scryfall_ids}})
    cards = await cursor.to_list(length=None)
    
    return {card.get("scryfall_id"): card for card in cards}


async def get_card_by_name(name: str) -> Optional[Dict[str, Any]]:

    card = await db.cards.find_one({"name": name})
    return card


async def create_card(card_data: Dict[str, Any]) -> Dict[str, Any]:

    # Garantir que o scryfall_id está presente
    if "scryfall_id" not in card_data:
        raise ValueError("card_data deve conter 'scryfall_id'")
    
    # Verificar se a carta já existe
    existing = await get_card_by_scryfall_id(card_data["scryfall_id"])
    if existing:
        return existing
    
    # Inserir nova carta
    result = await db.cards.insert_one(card_data)
    
    # Buscar e retornar a carta criada
    created_card = await db.cards.find_one({"_id": result.inserted_id})
    return created_card


async def create_or_update_card(card_data: Dict[str, Any]) -> Dict[str, Any]:

    if "scryfall_id" not in card_data:
        raise ValueError("card_data deve conter 'scryfall_id'")
    
    scryfall_id = card_data["scryfall_id"]
    
    result = await db.cards.update_one(
        {"scryfall_id": scryfall_id},
        {"$set": card_data},
        upsert=True
    )
    
    card = await get_card_by_scryfall_id(scryfall_id)
    return card


async def search_cards(
    name: Optional[str] = None,
    colors: Optional[list] = None,
    type_line: Optional[str] = None,
    rarity: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
) -> list[Dict[str, Any]]:

    filter_query = {}
    
    if name:
        # Busca parcial case-insensitive
        filter_query["name"] = {"$regex": name, "$options": "i"}
    
    if colors:
        # Busca cartas que contenham todas as cores especificadas
        filter_query["colors"] = {"$all": colors}
    
    if type_line:
        # Busca parcial no type_line
        filter_query["type_line"] = {"$regex": type_line, "$options": "i"}
    
    if rarity:
        filter_query["rarity"] = rarity.lower()
    
    # Buscar cartas
    cursor = db.cards.find(filter_query).skip(skip).limit(limit)
    cards = await cursor.to_list(length=limit)
    
    return cards


async def get_all_cards() -> list[Dict[str, Any]]:
    cursor = db.cards.find({})
    cards = await cursor.to_list(length=None)
    return cards


async def count_cards(
    name: Optional[str] = None,
    colors: Optional[list] = None,
    type_line: Optional[str] = None,
    rarity: Optional[str] = None
) -> int:

    filter_query = {}
    
    if name:
        filter_query["name"] = {"$regex": name, "$options": "i"}
    
    if colors:
        filter_query["colors"] = {"$all": colors}
    
    if type_line:
        filter_query["type_line"] = {"$regex": type_line, "$options": "i"}
    
    if rarity:
        filter_query["rarity"] = rarity.lower()
    
    count = await db.cards.count_documents(filter_query)
    return count

