"""
CRUD operations for Cards
Operações de banco de dados para cartas
"""
from typing import Optional, Dict, Any
from app.core.db import db


async def get_card_by_scryfall_id(scryfall_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca uma carta pelo scryfall_id
    
    Args:
        scryfall_id: ID único da carta na Scryfall
        
    Returns:
        Documento da carta ou None se não encontrada
    """
    card = await db.cards.find_one({"scryfall_id": scryfall_id})
    return card


async def get_card_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Busca uma carta pelo nome (busca exata)
    
    Args:
        name: Nome da carta
        
    Returns:
        Documento da carta ou None se não encontrada
    """
    card = await db.cards.find_one({"name": name})
    return card


async def create_card(card_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cria uma nova carta no banco de dados
    
    Args:
        card_data: Dados da carta (deve incluir scryfall_id)
        
    Returns:
        Documento da carta criada
    """
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
    """
    Cria uma carta ou atualiza se já existir (baseado no scryfall_id)
    
    Args:
        card_data: Dados da carta (deve incluir scryfall_id)
        
    Returns:
        Documento da carta criada ou atualizada
    """
    if "scryfall_id" not in card_data:
        raise ValueError("card_data deve conter 'scryfall_id'")
    
    scryfall_id = card_data["scryfall_id"]
    
    # Usar upsert: atualiza se existe, cria se não existe
    result = await db.cards.update_one(
        {"scryfall_id": scryfall_id},
        {"$set": card_data},
        upsert=True
    )
    
    # Retornar a carta atualizada/criada
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
    """
    Busca cartas com filtros opcionais
    
    Args:
        name: Filtrar por nome (busca parcial, case-insensitive)
        colors: Filtrar por cores (lista de cores)
        type_line: Filtrar por tipo (ex: "Creature", "Instant")
        rarity: Filtrar por raridade (ex: "common", "rare")
        limit: Número máximo de resultados
        skip: Número de resultados para pular (pagination)
        
    Returns:
        Lista de cartas encontradas
    """
    # Construir filtro dinamicamente
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


async def count_cards(filter_query: Optional[Dict[str, Any]] = None) -> int:
    """
    Conta o número de cartas no banco
    
    Args:
        filter_query: Filtro opcional para contar
        
    Returns:
        Número de cartas
    """
    if filter_query:
        count = await db.cards.count_documents(filter_query)
    else:
        count = await db.cards.count_documents({})
    return count

