import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.football_api import football_data_service

async def test_h2h():
    match_id = 538001
    print(f"Fetching H2H for match {match_id}...")
    try:
        data = await football_data_service.get_match_h2h(match_id)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_h2h())
