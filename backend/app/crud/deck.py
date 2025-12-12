"""
CRUD operations for Decks
Operações de banco de dados para decks
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.db import db


async def get_deck_by_id(deck_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca um deck pelo ID
    
    Args:
        deck_id: ID do deck (ObjectId como string)
        
    Returns:
        Documento do deck ou None se não encontrado
    """
    from bson import ObjectId
    
    try:
        deck = await db.decks.find_one({"_id": ObjectId(deck_id)})
        return deck
    except Exception:
        return None


async def get_deck_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Busca um deck pelo nome
    
    Args:
        name: Nome do deck
        
    Returns:
        Documento do deck ou None se não encontrado
    """
    deck = await db.decks.find_one({"name": name})
    return deck


async def create_deck(
    name: str,
    cards: List[Dict[str, Any]],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cria um novo deck no banco de dados
    
    Args:
        name: Nome do deck
        cards: Lista de cartas no formato [{"scryfall_id": "...", "quantity": 4}, ...]
        description: Descrição opcional do deck
        
    Returns:
        Documento do deck criado
    """
    deck_data = {
        "name": name,
        "cards": cards,
        "description": description,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.decks.insert_one(deck_data)
    
    # Buscar e retornar o deck criado
    created_deck = await db.decks.find_one({"_id": result.inserted_id})
    return created_deck


async def update_deck(
    deck_id: str,
    name: Optional[str] = None,
    cards: Optional[List[Dict[str, Any]]] = None,
    description: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Atualiza um deck existente
    
    Args:
        deck_id: ID do deck
        name: Novo nome (opcional)
        cards: Nova lista de cartas (opcional)
        description: Nova descrição (opcional)
        
    Returns:
        Documento do deck atualizado ou None se não encontrado
    """
    from bson import ObjectId
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if name:
        update_data["name"] = name
    if cards is not None:
        update_data["cards"] = cards
    if description is not None:
        update_data["description"] = description
    
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
    """
    Deleta um deck
    
    Args:
        deck_id: ID do deck
        
    Returns:
        True se deletado com sucesso, False caso contrário
    """
    from bson import ObjectId
    
    try:
        result = await db.decks.delete_one({"_id": ObjectId(deck_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def get_all_decks(limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Busca todos os decks (com paginação)
    
    Args:
        limit: Número máximo de resultados
        skip: Número de resultados para pular
        
    Returns:
        Lista de decks
    """
    cursor = db.decks.find().sort("created_at", -1).skip(skip).limit(limit)
    decks = await cursor.to_list(length=limit)
    return decks


async def get_deck_with_cards(deck_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca um deck e expande os dados das cartas associadas
    
    Args:
        deck_id: ID do deck
        
    Returns:
        Deck com dados completos das cartas ou None
    """
    deck = await get_deck_by_id(deck_id)
    
    if not deck:
        return None
    
    # Expandir dados das cartas
    expanded_cards = []
    for deck_card in deck.get("cards", []):
        scryfall_id = deck_card.get("scryfall_id")
        quantity = deck_card.get("quantity", 1)
        
        # Buscar dados completos da carta
        from app.crud.card import get_card_by_scryfall_id
        card_data = await get_card_by_scryfall_id(scryfall_id)
        
        if card_data:
            expanded_cards.append({
                **card_data,
                "quantity": quantity
            })
        else:
            # Se a carta não foi encontrada, manter apenas o scryfall_id
            expanded_cards.append({
                "scryfall_id": scryfall_id,
                "quantity": quantity,
                "error": "Card not found in database"
            })
    
    # Retornar deck com cartas expandidas
    deck["cards"] = expanded_cards
    return deck


async def count_decks() -> int:
    """
    Conta o número de decks no banco
    
    Returns:
        Número de decks
    """
    count = await db.decks.count_documents({})
    return count

