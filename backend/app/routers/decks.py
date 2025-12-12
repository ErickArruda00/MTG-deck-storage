from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from typing import Optional, Dict, Any
import httpx
from app.schemas import (
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckWithCardsResponse,
    DeckListResponse,
    AddCardToDeckRequest,
    UpdateCardQuantityRequest,
    BulkDeckImportRequest,
    BulkDeckImportResponse
)
from app.crud import deck as crud_deck
from app.services.scryfall import get_card_by_id, get_cards_by_ids
from app.utils import convert_id_to_string, convert_ids_in_list, is_valid_object_id

router = APIRouter()


async def _fetch_missing_card_names(deck: Dict[str, Any]) -> Dict[str, Any]:
    missing_scryfall_ids = []
    cards_without_name = []
    
    for i, card in enumerate(deck.get("cards", [])):
        name = card.get("name")
        if not name and "error" in card:
            scryfall_id = card.get("scryfall_id")
            if scryfall_id:
                missing_scryfall_ids.append(scryfall_id)
                cards_without_name.append((i, scryfall_id))
    
    scryfall_map = {}
    if missing_scryfall_ids:
        try:
            scryfall_results = await get_cards_by_ids(missing_scryfall_ids)
            for card_data in scryfall_results:
                scryfall_id = card_data.get("id")
                if scryfall_id:
                    scryfall_map[scryfall_id] = card_data.get("name", scryfall_id)
        except (httpx.HTTPStatusError, httpx.RequestError, Exception):
            pass
    
    for i, scryfall_id in cards_without_name:
        if scryfall_id in scryfall_map:
            deck["cards"][i]["name"] = scryfall_map[scryfall_id]
    
    return deck


def _format_export_text(deck: Dict[str, Any]) -> str:
    lines = []
    for card in deck.get("cards", []):
        quantity = card.get("quantity", 1)
        name = card.get("name")
        
        if not name:
            name = card.get("scryfall_id", "Unknown")
        
        lines.append(f"{quantity} {name}")
    
    return "\n".join(lines)


@router.post("/import-bulk", response_model=BulkDeckImportResponse, status_code=200)
async def import_decks_bulk(bulk_data: BulkDeckImportRequest):
    
    successful_decks = []
    failed_decks = []
    
    deck_names = [deck_data.name for deck_data in bulk_data.decks]
    existing_decks_map = await crud_deck.get_decks_by_names(deck_names)
    
    for deck_data in bulk_data.decks:
        try:
            if deck_data.name in existing_decks_map:
                failed_decks.append({
                    "name": deck_data.name,
                    "error": f"Já existe um deck com o nome '{deck_data.name}'"
                })
                continue
            
            deck_dict = {
                "name": deck_data.name,
                "format": deck_data.format,
                "cards": [
                    {
                        "scryfall_id": card.scryfall_id,
                        "quantity": card.quantity
                    }
                    for card in deck_data.cards
                ]
            }
            
            deck = await crud_deck.create_deck(
                name=deck_dict["name"],
                format=deck_dict["format"],
                cards=deck_dict["cards"]
            )
            
            convert_id_to_string(deck)
            
            existing_decks_map[deck_data.name] = deck
            successful_decks.append(deck)
            
        except Exception as e:
            failed_decks.append({
                "name": deck_data.name,
                "error": f"Erro ao importar: {str(e)}"
            })
    
    return {
        "total": len(bulk_data.decks),
        "success": len(successful_decks),
        "failed": len(failed_decks),
        "successful_decks": successful_decks,
        "failed_decks": failed_decks
    }


@router.post("/", response_model=DeckResponse, status_code=201)
async def create_deck(deck_data: DeckCreate):

    existing = await crud_deck.get_deck_by_name(deck_data.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um deck com o nome '{deck_data.name}'"
        )
    
    deck_dict = {
        "name": deck_data.name,
        "format": deck_data.format,
        "cards": [
            {
                "scryfall_id": card.scryfall_id,
                "quantity": card.quantity
            }
            for card in deck_data.cards
        ]
    }
    
    deck = await crud_deck.create_deck(
        name=deck_dict["name"],
        format=deck_dict["format"],
        cards=deck_dict["cards"]
    )
    
    convert_id_to_string(deck)
    
    return deck


@router.get("/backup")
async def backup_all_decks():
    
    decks = await crud_deck.get_all_decks(limit=10000, skip=0)
    
    export_data = []
    for deck in decks:
        export_data.append({
            "name": deck.get("name"),
            "format": deck.get("format"),
            "cards": [
                {
                    "scryfall_id": card.get("scryfall_id"),
                    "quantity": card.get("quantity", 1)
                }
                for card in deck.get("cards", [])
            ]
        })
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": 'attachment; filename="all_decks.json"'
        }
    )


@router.get("/", response_model=DeckListResponse)
async def list_decks(
    format: Optional[str] = Query(None, description="Filtrar por formato (ex: commander, standard, modern)"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de resultados"),
    skip: int = Query(0, ge=0, description="Número de resultados para pular")
):
    decks = await crud_deck.get_all_decks(format=format, limit=limit, skip=skip)
    total = await crud_deck.count_decks(format=format)
    
    convert_ids_in_list(decks)
    
    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "decks": decks
    }


@router.post("/{deck_id}/cards", response_model=DeckResponse)
async def add_card_to_deck(deck_id: str, card_data: AddCardToDeckRequest):
    
    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )
    
    existing_deck = await crud_deck.get_deck_by_id(deck_id)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    updated_deck = await crud_deck.add_card_to_deck(
        deck_id=deck_id,
        scryfall_id=card_data.scryfall_id,
        quantity=card_data.quantity
    )
    
    if not updated_deck:
        raise HTTPException(
            status_code=500,
            detail="Erro ao adicionar carta ao deck"
        )
    
    convert_id_to_string(updated_deck)
    
    return updated_deck


@router.delete("/{deck_id}/cards/{scryfall_id}", response_model=DeckResponse)
async def remove_card_from_deck(deck_id: str, scryfall_id: str):
    
    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )
    
    existing_deck = await crud_deck.get_deck_by_id(deck_id)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    updated_deck = await crud_deck.remove_card_from_deck(
        deck_id=deck_id,
        scryfall_id=scryfall_id
    )
    
    if not updated_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Carta com scryfall_id '{scryfall_id}' não encontrada no deck ou deck ficaria vazio"
        )
    
    convert_id_to_string(updated_deck)
    
    return updated_deck


@router.put("/{deck_id}/cards/{scryfall_id}", response_model=DeckResponse)
async def update_card_quantity(deck_id: str, scryfall_id: str, quantity_data: UpdateCardQuantityRequest):
    
    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )
    
    existing_deck = await crud_deck.get_deck_by_id(deck_id)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    updated_deck = await crud_deck.update_card_quantity_in_deck(
        deck_id=deck_id,
        scryfall_id=scryfall_id,
        quantity=quantity_data.quantity
    )
    
    if not updated_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Carta com scryfall_id '{scryfall_id}' não encontrada no deck"
        )
    
    convert_id_to_string(updated_deck)
    
    return updated_deck


@router.get("/{deck_id}/export-json")
async def export_deck_json(deck_id: str):
    
    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )
    
    deck = await crud_deck.get_deck_by_id(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    export_data = {
        "name": deck.get("name"),
        "format": deck.get("format"),
        "cards": [
            {
                "scryfall_id": card.get("scryfall_id"),
                "quantity": card.get("quantity", 1)
            }
            for card in deck.get("cards", [])
        ]
    }
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f'attachment; filename="deck_{deck.get("name", "export")}.json"'
        }
    )


@router.get("/export-by-name/{deck_name}/json")
async def export_deck_by_name_json(deck_name: str):
    
    deck_by_name = await crud_deck.get_deck_by_name(deck_name)
    
    if not deck_by_name:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    export_data = {
        "name": deck_by_name.get("name"),
        "format": deck_by_name.get("format"),
        "cards": [
            {
                "scryfall_id": card.get("scryfall_id"),
                "quantity": card.get("quantity", 1)
            }
            for card in deck_by_name.get("cards", [])
        ]
    }
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f'attachment; filename="deck_{deck_by_name.get("name", "export")}.json"'
        }
    )


@router.get("/export-by-name/{deck_name}")
async def export_deck_by_name(deck_name: str):
    
    deck_by_name = await crud_deck.get_deck_by_name(deck_name)
    
    if not deck_by_name:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    deck_id = str(deck_by_name["_id"])
    deck = await crud_deck.get_deck_with_cards(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    deck = await _fetch_missing_card_names(deck)
    export_text = _format_export_text(deck)
    
    return Response(
        content=export_text,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="deck_{deck.get("name", "export")}.txt"'
        }
    )


@router.get("/{deck_id}/export")
async def export_deck(deck_id: str):
    
    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )
    
    deck = await crud_deck.get_deck_with_cards(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    deck = await _fetch_missing_card_names(deck)
    export_text = _format_export_text(deck)
    
    return Response(
        content=export_text,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="deck_{deck.get("name", "export")}.txt"'
        }
    )


@router.get("/by-name/{deck_name}", response_model=DeckWithCardsResponse)
async def get_deck_by_name(deck_name: str):
    
    deck_by_name = await crud_deck.get_deck_by_name(deck_name)
    
    if not deck_by_name:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    deck_id = str(deck_by_name["_id"])
    deck = await crud_deck.get_deck_with_cards(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    convert_id_to_string(deck)
    if "_id" in deck:
        deck["deck_id"] = deck["_id"]
    
    convert_ids_in_list(deck.get("cards", []))
    
    return deck


@router.get("/{deck_id}", response_model=DeckWithCardsResponse)
async def get_deck(deck_id: str):

    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )

    deck = await crud_deck.get_deck_with_cards(deck_id)
    
    if not deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    convert_id_to_string(deck)
    if "_id" in deck:
        deck["deck_id"] = deck["_id"]
    
    convert_ids_in_list(deck.get("cards", []))
    
    return deck


@router.put("/by-name/{deck_name}", response_model=DeckResponse)
async def update_deck_by_name(deck_name: str, deck_data: DeckUpdate):
    
    existing_deck = await crud_deck.get_deck_by_name(deck_name)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    deck_id = str(existing_deck["_id"])
    
    if deck_data.name and deck_data.name != existing_deck.get("name"):
        name_exists = await crud_deck.get_deck_by_name(deck_data.name)
        if name_exists and str(name_exists["_id"]) != deck_id:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um deck com o nome '{deck_data.name}'"
            )
    
    update_dict = {}
    if deck_data.name:
        update_dict["name"] = deck_data.name
    if deck_data.format:
        update_dict["format"] = deck_data.format
    if deck_data.cards:
        update_dict["cards"] = [
            {
                "scryfall_id": card.scryfall_id,
                "quantity": card.quantity
            }
            for card in deck_data.cards
        ]
    
    updated_deck = await crud_deck.update_deck(
        deck_id=deck_id,
        name=update_dict.get("name"),
        format=update_dict.get("format"),
        cards=update_dict.get("cards")
    )
    
    if not updated_deck:
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar deck"
        )
    
    convert_id_to_string(updated_deck)
    
    return updated_deck


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(deck_id: str, deck_data: DeckUpdate):

    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )

    existing_deck = await crud_deck.get_deck_by_id(deck_id)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    
    if deck_data.name and deck_data.name != existing_deck.get("name"):
        name_exists = await crud_deck.get_deck_by_name(deck_data.name)
        if name_exists and str(name_exists["_id"]) != deck_id:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe um deck com o nome '{deck_data.name}'"
            )
    
    update_dict = {}
    if deck_data.name:
        update_dict["name"] = deck_data.name
    if deck_data.format:
        update_dict["format"] = deck_data.format
    if deck_data.cards:
        update_dict["cards"] = [
            {
                "scryfall_id": card.scryfall_id,
                "quantity": card.quantity
            }
            for card in deck_data.cards
        ]
    
    updated_deck = await crud_deck.update_deck(
        deck_id=deck_id,
        name=update_dict.get("name"),
        format=update_dict.get("format"),
        cards=update_dict.get("cards")
    )
    
    if not updated_deck:
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar deck"
        )
    
    convert_id_to_string(updated_deck)
    
    return updated_deck


@router.delete("/by-name/{deck_name}", status_code=204)
async def delete_deck_by_name(deck_name: str):
    
    existing_deck = await crud_deck.get_deck_by_name(deck_name)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com nome '{deck_name}' não encontrado"
        )
    
    deck_id = str(existing_deck["_id"])
    deleted = await crud_deck.delete_deck(deck_id)
    
    if not deleted:
        raise HTTPException(
            status_code=500,
            detail="Erro ao deletar deck"
        )
    return None


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(deck_id: str):

    if not is_valid_object_id(deck_id):
        raise HTTPException(
            status_code=400,
            detail=f"ID de deck inválido: '{deck_id}'"
        )

    existing_deck = await crud_deck.get_deck_by_id(deck_id)
    if not existing_deck:
        raise HTTPException(
            status_code=404,
            detail=f"Deck com ID '{deck_id}' não encontrado"
        )
    deleted = await crud_deck.delete_deck(deck_id)
    
    if not deleted:
        raise HTTPException(
            status_code=500,
            detail="Erro ao deletar deck"
        )
    return None
