from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class CardBase(BaseModel):
    name: str = Field(..., description="Nome da carta")
    scryfall_id: str = Field(..., description="ID único da carta na Scryfall (UUID)")
    oracle_id: Optional[str] = Field(None, description="ID do texto Oracle da carta (UUID)")
    mana_cost: Optional[str] = Field(None, description="Custo de mana (ex: '{2}{R}{R}')")
    cmc: Optional[float] = Field(None, description="Converted Mana Cost")
    type_line: Optional[str] = Field(None, description="Tipo da carta (ex: 'Creature — Human Wizard')")
    oracle_text: Optional[str] = Field(None, description="Texto da carta")
    power: Optional[str] = Field(None, description="Poder da criatura")
    toughness: Optional[str] = Field(None, description="Resistência da criatura")
    colors: Optional[List[str]] = Field(
        default_factory=list, 
        description="Cores da carta (ex: ['R', 'U']) - W, U, B, R, G"
    )
    color_identity: Optional[List[str]] = Field(
        default_factory=list, 
        description="Identidade de cor (ex: ['R'])"
    )
    rarity: Optional[str] = Field(
        None, 
        description="Raridade: common, uncommon, rare, mythic, special, bonus"
    )
    set_name: Optional[str] = Field(None, description="Nome do set")
    set_code: Optional[str] = Field(None, description="Código do set (ex: 'lea')")
    image_uris: Optional[dict] = Field(
        None, 
        description="URIs das imagens: {small, normal, large, png, art_crop, border_crop}"
    )
    prices: Optional[dict] = Field(
        None, 
        description="Preços: {usd, usd_foil, eur, eur_foil, tix}"
    )


class CardCreate(CardBase):
    pass


class CardResponse(CardBase):
    id: Optional[str] = Field(None, alias="_id", description="ID do documento no MongoDB")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class CardImportRequest(BaseModel):
    name: str = Field(..., description="Nome exato da carta para buscar na Scryfall")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lightning Bolt"
            }
        }


class CardSearchRequest(BaseModel):
    name: Optional[str] = Field(None, description="Buscar por nome (busca parcial)")
    colors: Optional[List[str]] = Field(None, description="Filtrar por cores (ex: ['R', 'U'])")
    type_line: Optional[str] = Field(None, description="Filtrar por tipo (ex: 'Creature')")
    rarity: Optional[str] = Field(None, description="Filtrar por raridade")
    limit: int = Field(50, ge=1, le=100, description="Número máximo de resultados")
    skip: int = Field(0, ge=0, description="Número de resultados para pular (pagination)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "bolt",
                "colors": ["R"],
                "limit": 10,
                "skip": 0
            }
        }


class CardListResponse(BaseModel):
    total: int = Field(..., description="Total de cartas encontradas")
    limit: int = Field(..., description="Limite de resultados")
    skip: int = Field(..., description="Resultados pulados")
    cards: List[CardResponse] = Field(..., description="Lista de cartas")


class CardBulkImportRequest(BaseModel):
    names: List[str] = Field(..., min_items=1, max_items=100, description="Lista de nomes de cartas para importar (máximo 100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "names": ["Lightning Bolt", "Counterspell", "Dark Ritual"]
            }
        }


class CardBulkImportResponse(BaseModel):
    total: int = Field(..., description="Total de cartas processadas")
    success: int = Field(..., description="Número de cartas importadas com sucesso")
    failed: int = Field(..., description="Número de cartas que falharam")
    successful_cards: List[CardResponse] = Field(..., description="Cartas importadas com sucesso")
    failed_cards: List[dict] = Field(..., description="Cartas que falharam com motivo do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "success": 2,
                "failed": 1,
                "successful_cards": [],
                "failed_cards": [
                    {"name": "Invalid Card", "error": "Card not found"}
                ]
            }
        }

