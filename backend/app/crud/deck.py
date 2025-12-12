from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.db import db


async def get_deck_by_id(deck_id: str) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    from bson.errors import InvalidId
    
    try:
        deck = await db.decks.find_one({"_id": ObjectId(deck_id)})
        return deck
    except (InvalidId, ValueError, TypeError):
        return None


async def get_deck_by_name(name: str) -> Optional[Dict[str, Any]]:
    deck = await db.decks.find_one({"name": name})
    return deck


async def get_decks_by_names(names: List[str]) -> Dict[str, Dict[str, Any]]:
    if not names:
        return {}
    
    cursor = db.decks.find({"name": {"$in": names}})
    decks = await cursor.to_list(length=None)
    
    return {deck.get("name"): deck for deck in decks}


async def create_deck(
    name: str,
    format: str,
    cards: List[Dict[str, Any]]
) -> Dict[str, Any]:
    deck_data = {
        "name": name,
        "format": format,
        "cards": cards,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.decks.insert_one(deck_data)
    created_deck = await db.decks.find_one({"_id": result.inserted_id})
    return created_deck


async def update_deck(
    deck_id: str,
    name: Optional[str] = None,
    format: Optional[str] = None,
    cards: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if name:
        update_data["name"] = name
    if format:
        update_data["format"] = format
    if cards is not None:
        update_data["cards"] = cards
    
    try:
        result = await db.decks.update_one(
            {"_id": ObjectId(deck_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await get_deck_by_id(deck_id)
        return None
    except Exception:
        return None


async def delete_deck(deck_id: str) -> bool:
    from bson import ObjectId
    
    try:
        result = await db.decks.delete_one({"_id": ObjectId(deck_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def get_all_decks(format: Optional[str] = None, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    query = {}
    if format:
        query["format"] = format
    
    cursor = db.decks.find(query).sort("created_at", -1).skip(skip).limit(limit)
    decks = await cursor.to_list(length=limit)
    return decks


async def get_deck_with_cards(deck_id: str) -> Optional[Dict[str, Any]]:
    deck = await get_deck_by_id(deck_id)
    
    if not deck:
        return None
    
    deck_cards = deck.get("cards", [])
    if not deck_cards:
        deck["cards"] = []
        return deck
    
    scryfall_ids = [card.get("scryfall_id") for card in deck_cards if card.get("scryfall_id")]
    
    from app.crud.card import get_cards_by_scryfall_ids
    cards_map = await get_cards_by_scryfall_ids(scryfall_ids)
    
    expanded_cards = []
    for deck_card in deck_cards:
        scryfall_id = deck_card.get("scryfall_id")
        quantity = deck_card.get("quantity", 1)
        
        card_data = cards_map.get(scryfall_id)
        
        if card_data:
            expanded_cards.append({
                **card_data,
                "quantity": quantity
            })
        else:
            expanded_cards.append({
                "scryfall_id": scryfall_id,
                "quantity": quantity,
                "error": "Card not found in database"
            })
    
    deck["cards"] = expanded_cards
    return deck


async def count_decks(format: Optional[str] = None) -> int:
    query = {}
    if format:
        query["format"] = format
    
    count = await db.decks.count_documents(query)
    return count


async def add_card_to_deck(
    deck_id: str,
    scryfall_id: str,
    quantity: int
) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    
    try:
        deck = await get_deck_by_id(deck_id)
        if not deck:
            return None
        
        cards = deck.get("cards", [])
        
        card_found = False
        for card in cards:
            if card.get("scryfall_id") == scryfall_id:
                card["quantity"] = card.get("quantity", 0) + quantity
                card_found = True
                break
        
        if not card_found:
            cards.append({
                "scryfall_id": scryfall_id,
                "quantity": quantity
            })
        
        result = await db.decks.update_one(
            {"_id": ObjectId(deck_id)},
            {
                "$set": {
                    "cards": cards,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await get_deck_by_id(deck_id)
        return None
    except Exception:
        return None


async def remove_card_from_deck(
    deck_id: str,
    scryfall_id: str
) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    
    try:
        deck = await get_deck_by_id(deck_id)
        if not deck:
            return None
        
        cards = deck.get("cards", [])
        
        updated_cards = [
            card for card in cards
            if card.get("scryfall_id") != scryfall_id
        ]
        
        if len(updated_cards) == len(cards):
            return None
        
        if len(updated_cards) == 0:
            return None
        
        result = await db.decks.update_one(
            {"_id": ObjectId(deck_id)},
            {
                "$set": {
                    "cards": updated_cards,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await get_deck_by_id(deck_id)
        return None
    except Exception:
        return None


async def update_card_quantity_in_deck(
    deck_id: str,
    scryfall_id: str,
    quantity: int
) -> Optional[Dict[str, Any]]:
    from bson import ObjectId
    
    try:
        deck = await get_deck_by_id(deck_id)
        if not deck:
            return None
        
        cards = deck.get("cards", [])
        
        card_found = False
        for card in cards:
            if card.get("scryfall_id") == scryfall_id:
                card["quantity"] = quantity
                card_found = True
                break
        
        if not card_found:
            return None
        
        result = await db.decks.update_one(
            {"_id": ObjectId(deck_id)},
            {
                "$set": {
                    "cards": cards,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await get_deck_by_id(deck_id)
        return None
    except Exception:
        return None

