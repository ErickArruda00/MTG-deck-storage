import httpx
from typing import List, Dict, Any

async def get_card_data(name: str):
    url = f"https://api.scryfall.com/cards/named?exact={name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_card_by_id(scryfall_id: str):
    url = f"https://api.scryfall.com/cards/{scryfall_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_cards_collection(names: List[str]) -> List[Dict[str, Any]]:
    url = "https://api.scryfall.com/cards/collection"
    max_batch_size = 75
    all_results = []
    
    for i in range(0, len(names), max_batch_size):
        batch = names[i:i + max_batch_size]
        identifiers = [{"name": name} for name in batch]
        payload = {"identifiers": identifiers}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            all_results.extend(data.get("data", []))
    
    return all_results


async def get_cards_by_ids(scryfall_ids: List[str]) -> List[Dict[str, Any]]:
    url = "https://api.scryfall.com/cards/collection"
    max_batch_size = 75
    all_results = []
    
    for i in range(0, len(scryfall_ids), max_batch_size):
        batch = scryfall_ids[i:i + max_batch_size]
        identifiers = [{"id": scryfall_id} for scryfall_id in batch]
        payload = {"identifiers": identifiers}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            all_results.extend(data.get("data", []))
    
    return all_results