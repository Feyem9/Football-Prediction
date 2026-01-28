
import requests
import json

def test_apex_report():
    match_id = 111  # Use a known match ID or get one from DB
    url = f"http://localhost:8000/api/v1/matches/{match_id}/apex30-report"
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_apex_report()
