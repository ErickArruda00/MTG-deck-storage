from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DeckCard(BaseModel):
    scryfall_id: str = Field(..., description="ID da carta (scryfall_id)")
    quantity: int = Field(..., ge=1, description="Quantidade da carta no deck")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scryfall_id": "abc123",
                "quantity": 4
            }
        }


class DeckBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200, description="Nome do deck (minimo 3 caracteres)")
    format: str = Field(..., description="Formato do deck (ex: commander, standard, modern, legacy, vintage, pauper, bulk)")
    cards: List[DeckCard] = Field(..., description="Lista de cartas do deck")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Red Deck Wins",
                "format": "commander",
                "cards": [
                    {"scryfall_id": "abc123", "quantity": 4},
                    {"scryfall_id": "def456", "quantity": 2}
                ]
            }
        }


class DeckCreate(DeckBase):
    pass


class DeckUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200, description="Nome do deck (minimo 3 caracteres)")
    format: Optional[str] = Field(None, description="Formato do deck (ex: commander, standard, modern, bulk)")
    cards: Optional[List[DeckCard]] = Field(None, description="Lista de cartas do deck")


class DeckCardExpanded(DeckCard):
    pass


class DeckResponse(DeckBase):
    id: str = Field(..., alias="_id", description="ID do deck no MongoDB")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Red Deck Wins",
                "format": "commander",
                "cards": [
                    {"scryfall_id": "abc123", "quantity": 4}
                ],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class DeckWithCardsResponse(BaseModel):
    id: str = Field(..., alias="_id", description="ID do deck")
    deck_id: str = Field(..., description="ID do deck")
    name: str = Field(..., description="Nome do deck")
    format: str = Field(..., description="Formato do deck")
    cards: List[dict] = Field(..., description="Lista de cartas com dados completos")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class DeckListResponse(BaseModel):
    total: int = Field(..., description="Total de decks encontrados")
    limit: int = Field(..., description="Limite de resultados")
    skip: int = Field(..., description="Resultados pulados")
    decks: List[DeckResponse] = Field(..., description="Lista de decks")


class AddCardToDeckRequest(BaseModel):
    scryfall_id: str = Field(..., description="ID da carta (scryfall_id)")
    quantity: int = Field(..., ge=1, description="Quantidade da carta a adicionar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scryfall_id": "abc123",
                "quantity": 2
            }
        }


class UpdateCardQuantityRequest(BaseModel):
    quantity: int = Field(..., ge=1, description="Nova quantidade da carta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 4
            }
        }


class BulkDeckImportRequest(BaseModel):
    decks: List[DeckCreate] = Field(..., min_items=1, max_items=100, description="Lista de decks para importar (máximo 100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decks": [
                    {
                        "name": "Deck 1",
                        "format": "commander",
                        "cards": [
                            {"scryfall_id": "abc123", "quantity": 4}
                        ]
                    },
                    {
                        "name": "Deck 2",
                        "format": "standard",
                        "cards": [
                            {"scryfall_id": "def456", "quantity": 2}
                        ]
                    }
                ]
            }
        }


class BulkDeckImportResponse(BaseModel):
    total: int = Field(..., description="Total de decks processados")
    success: int = Field(..., description="Número de decks importados com sucesso")
    failed: int = Field(..., description="Número de decks que falharam")
    successful_decks: List[DeckResponse] = Field(..., description="Decks importados com sucesso")
    failed_decks: List[dict] = Field(..., description="Decks que falharam com motivo do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "success": 1,
                "failed": 1,
                "successful_decks": [],
                "failed_decks": [
                    {"name": "Deck Duplicado", "error": "Já existe um deck com esse nome"}
                ]
            }
        }

