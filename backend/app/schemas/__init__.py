"""
Schemas module - Schemas Pydantic para validação de dados
"""
from app.schemas.card import (
    CardBase,
    CardCreate,
    CardResponse,
    CardImportRequest,
    CardSearchRequest,
    CardListResponse
)
from app.schemas.deck import (
    DeckCard,
    DeckBase,
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckWithCardsResponse,
    DeckListResponse
)

__all__ = [
    # Card schemas
    "CardBase",
    "CardCreate",
    "CardResponse",
    "CardImportRequest",
    "CardSearchRequest",
    "CardListResponse",
    # Deck schemas
    "DeckCard",
    "DeckBase",
    "DeckCreate",
    "DeckUpdate",
    "DeckResponse",
    "DeckWithCardsResponse",
    "DeckListResponse",
]

