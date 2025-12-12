"""
Schemas para Decks
Define a estrutura de dados para validação de decks
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DeckCard(BaseModel):
    """Schema para uma carta dentro de um deck"""
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
    """Schema base para deck"""
    name: str = Field(..., min_length=1, max_length=200, description="Nome do deck")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do deck")
    cards: List[DeckCard] = Field(..., min_items=1, description="Lista de cartas do deck")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Red Deck Wins",
                "description": "Um deck agressivo vermelho",
                "cards": [
                    {"scryfall_id": "abc123", "quantity": 4},
                    {"scryfall_id": "def456", "quantity": 2}
                ]
            }
        }


class DeckCreate(DeckBase):
    """Schema para criar um deck"""
    pass


class DeckUpdate(BaseModel):
    """Schema para atualizar um deck - todos os campos são opcionais"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Nome do deck")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do deck")
    cards: Optional[List[DeckCard]] = Field(None, min_items=1, description="Lista de cartas do deck")


class DeckCardExpanded(DeckCard):
    """Schema para carta expandida no deck (com dados completos da carta)"""
    # Campos da carta serão adicionados dinamicamente
    pass


class DeckResponse(DeckBase):
    """Schema de resposta da API para deck"""
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
                "description": "Um deck agressivo vermelho",
                "cards": [
                    {"scryfall_id": "abc123", "quantity": 4}
                ],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class DeckWithCardsResponse(BaseModel):
    """Schema de resposta para deck com cartas expandidas"""
    id: str = Field(..., alias="_id", description="ID do deck")
    name: str = Field(..., description="Nome do deck")
    description: Optional[str] = Field(None, description="Descrição do deck")
    cards: List[dict] = Field(..., description="Lista de cartas com dados completos")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de última atualização")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class DeckListResponse(BaseModel):
    """Schema de resposta para lista de decks"""
    total: int = Field(..., description="Total de decks encontrados")
    limit: int = Field(..., description="Limite de resultados")
    skip: int = Field(..., description="Resultados pulados")
    decks: List[DeckResponse] = Field(..., description="Lista de decks")

