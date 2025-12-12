from fastapi import APIRouter, HTTPException, Query
from typing import Optional

import httpx
from app.core.db import db
from app.schemas import (
    CardImportRequest,
    CardBulkImportRequest,
    CardBulkImportResponse,
    CardResponse,
    CardSearchRequest,
    CardListResponse
)
from app.crud import card as crud_card
from app.services.scryfall import get_card_data, get_cards_collection
from app.utils import map_scryfall_to_card, convert_id_to_string, convert_ids_in_list

router = APIRouter()


@router.get("/test")
async def test_mongo():
    count = await db.cards.count_documents({})
    return {"mongo_status": "ok", "total_cards": count}


@router.post("/import", response_model=CardResponse, status_code=201)
async def import_card(card_data: CardImportRequest):
    try:
        scryfall_data = await get_card_data(card_data.name)
        card_data_mapped = map_scryfall_to_card(scryfall_data)
        card = await crud_card.create_or_update_card(card_data_mapped)
        convert_id_to_string(card)
        
        return card
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Carta '{card_data.name}' não encontrada na Scryfall"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao importar carta: {str(e)}"
        )


@router.get("/{scryfall_id}", response_model=CardResponse)
async def get_card(scryfall_id: str):
    card = await crud_card.get_card_by_scryfall_id(scryfall_id)
    
    if not card:
        raise HTTPException(
            status_code=404,
            detail=f"Carta com scryfall_id '{scryfall_id}' não encontrada"
        )
    
    convert_id_to_string(card)
    
    return card


@router.get("/", response_model=CardListResponse)
async def search_cards(
    name: Optional[str] = Query(None, description="Buscar por nome (busca parcial)"),
    colors: Optional[str] = Query(None, description="Filtrar por cores (ex: R,U ou R,U,W)"),
    type_line: Optional[str] = Query(None, description="Filtrar por tipo (ex: Creature)"),
    rarity: Optional[str] = Query(None, description="Filtrar por raridade"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    skip: int = Query(0, ge=0, description="Número de resultados para pular")
):
    colors_list = None
    if colors:
        colors_list = [c.strip().upper() for c in colors.split(",")]
    
    cards = await crud_card.search_cards(
        name=name,
        colors=colors_list,
        type_line=type_line,
        rarity=rarity,
        limit=limit,
        skip=skip
    )
    
    total = await crud_card.count_cards(
        name=name,
        colors=colors_list,
        type_line=type_line,
        rarity=rarity
    )
    
    convert_ids_in_list(cards)
    
    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "cards": cards
    }


@router.get("/all", response_model=CardListResponse)
async def get_all_cards(
    limit: int = Query(100, ge=1, le=100, description="Número máximo de resultados (máximo 100, padrão: 100)"),
    skip: int = Query(0, ge=0, description="Número de resultados para pular (padrão: 0)")
):
    
    cards = await crud_card.search_cards(
        name=None,
        colors=None,
        type_line=None,
        rarity=None,
        limit=limit,
        skip=skip
    )
    
    total = await crud_card.count_cards()
    
    convert_ids_in_list(cards)
    
    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "cards": cards
    }


@router.get("/count/total")
async def count_cards():

    count = await crud_card.count_cards()
    return {"total_cards": count}


@router.post("/import-bulk", response_model=CardBulkImportResponse, status_code=200)
async def import_cards_bulk(bulk_data: CardBulkImportRequest):
    
    successful_cards = []
    failed_cards = []
    
    try:
        scryfall_results = await get_cards_collection(bulk_data.names)
        
        scryfall_map = {}
        for card_data in scryfall_results:
            card_name = card_data.get("name", "").lower()
            scryfall_map[card_name] = card_data
        
        for name in bulk_data.names:
            try:
                name_lower = name.lower()
                scryfall_data = scryfall_map.get(name_lower)
                
                if not scryfall_data:
                    failed_cards.append({
                        "name": name,
                        "error": f"Carta '{name}' não encontrada na Scryfall"
                    })
                    continue
                
                card_data_mapped = map_scryfall_to_card(scryfall_data)
                card = await crud_card.create_or_update_card(card_data_mapped)
                
                convert_id_to_string(card)
                
                successful_cards.append(card)
                
            except ValueError as e:
                failed_cards.append({
                    "name": name,
                    "error": str(e)
                })
            except Exception as e:
                failed_cards.append({
                    "name": name,
                    "error": f"Erro ao importar: {str(e)}"
                })
    
    except httpx.HTTPStatusError as e:
        for name in bulk_data.names:
            failed_cards.append({
                "name": name,
                "error": f"Erro na requisição para Scryfall: {e.response.status_code}"
            })
    except Exception as e:
        for name in bulk_data.names:
            failed_cards.append({
                "name": name,
                "error": f"Erro ao buscar cartas: {str(e)}"
            })
    
    return {
        "total": len(bulk_data.names),
        "success": len(successful_cards),
        "failed": len(failed_cards),
        "successful_cards": successful_cards,
        "failed_cards": failed_cards
    }