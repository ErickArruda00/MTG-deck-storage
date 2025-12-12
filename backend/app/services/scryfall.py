import httpx

async def get_card_data(name: str):
    url = f"https://api.scryfall.com/cards/named?exact={name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
