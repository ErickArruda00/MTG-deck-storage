"""
Schemas para Cartas (Cards)
Define a estrutura de dados para validação de cartas
"""
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class CardBase(BaseModel):
    """Schema base para carta - campos comuns"""
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
    """Schema para criar uma carta - herda todos os campos de CardBase"""
    pass


class CardResponse(CardBase):
    """Schema de resposta da API - inclui campos adicionais do MongoDB"""
    id: Optional[str] = Field(None, alias="_id", description="ID do documento no MongoDB")
    
    class Config:
        """Configuração do Pydantic"""
        populate_by_name = True  # Permite usar tanto _id quanto id
        from_attributes = True


class CardImportRequest(BaseModel):
    """Schema para requisição de importação de carta"""
    name: str = Field(..., description="Nome exato da carta para buscar na Scryfall")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Lightning Bolt"
            }
        }


class CardSearchRequest(BaseModel):
    """Schema para busca de cartas com filtros"""
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
    """Schema de resposta para lista de cartas"""
    total: int = Field(..., description="Total de cartas encontradas")
    limit: int = Field(..., description="Limite de resultados")
    skip: int = Field(..., description="Resultados pulados")
    cards: List[CardResponse] = Field(..., description="Lista de cartas")

