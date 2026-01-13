import asyncio
import os
import httpx
from dotenv import load_dotenv

async def test_api():
    load_dotenv("../../.env")
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    url = "https://api.football-data.org/v4/competitions/SA/matches?limit=1"
    headers = {"X-Auth-Token": api_key}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Data: {response.json().get('competition', {}).get('name')}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
