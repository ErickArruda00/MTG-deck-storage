"""
Utilitário para mapear dados da API Scryfall para o formato do banco de dados
"""
from typing import Dict, Any


def map_scryfall_to_card(scryfall_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeia dados da API Scryfall para o formato do banco de dados.
    
    A API Scryfall retorna muitos campos, mas nem todos são necessários.
    Esta função mapeia apenas os campos relevantes e renomeia alguns campos
    para manter consistência no banco de dados.
    
    Args:
        scryfall_data: Dados retornados pela API Scryfall (JSON)
        
    Returns:
        Dicionário com dados mapeados para o formato do banco de dados
        
    Exemplo:
        >>> scryfall_response = {
        ...     "id": "abc123",
        ...     "name": "Lightning Bolt",
        ...     "set": "lea",
        ...     "colors": ["R"]
        ... }
        >>> mapped = map_scryfall_to_card(scryfall_response)
        >>> mapped["scryfall_id"]  # "abc123"
        >>> mapped["set_code"]     # "lea"
    """
    # Mapear campos principais
    mapped = {
        # IDs
        "scryfall_id": scryfall_data.get("id"),  # id → scryfall_id
        "oracle_id": scryfall_data.get("oracle_id"),
        
        # Informações básicas
        "name": scryfall_data.get("name"),
        "mana_cost": scryfall_data.get("mana_cost"),
        "cmc": scryfall_data.get("cmc"),
        "type_line": scryfall_data.get("type_line"),
        "oracle_text": scryfall_data.get("oracle_text"),
        
        # Atributos de criatura
        "power": scryfall_data.get("power"),
        "toughness": scryfall_data.get("toughness"),
        
        # Cores (já vem como array da API: ["W", "U", "B", "R", "G"])
        "colors": scryfall_data.get("colors", []),
        "color_identity": scryfall_data.get("color_identity", []),
        
        # Raridade e set
        "rarity": scryfall_data.get("rarity"),
        "set_name": scryfall_data.get("set_name"),
        "set_code": scryfall_data.get("set"),  # set → set_code
        
        # Imagens e preços (objetos completos)
        "image_uris": scryfall_data.get("image_uris"),
        "prices": scryfall_data.get("prices"),
    }
    
    # Validar que scryfall_id está presente (obrigatório)
    if not mapped["scryfall_id"]:
        raise ValueError("Dados da Scryfall não contêm 'id' (scryfall_id obrigatório)")
    
    if not mapped["name"]:
        raise ValueError("Dados da Scryfall não contêm 'name' (nome obrigatório)")
    
    return mapped

