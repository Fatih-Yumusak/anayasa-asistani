import requests
import json

def test_legislation_filter():
    base_url = "http://localhost:8000/api/legislation"
    
    # Test 1: Anayasa
    print("Testing Source: Anayasa...")
    res = requests.get(base_url, params={"source": "Anayasa"})
    data = res.json()
    articles = data.get("articles", [])
    print(f"Found {len(articles)} articles.")
    if articles and articles[0]['metadata']['source'] == "Anayasa":
        print("✅ Source check passed.")
    else:
        print("❌ Source check failed.")

    # Test 2: TIHEK Kanunu
    print("\nTesting Source: TIHEK Kanunu...")
    res = requests.get(base_url, params={"source": "TIHEK Kanunu"})
    data = res.json()
    articles = data.get("articles", [])
    print(f"Found {len(articles)} articles.")
    if articles and articles[0]['metadata']['source'] == "TIHEK Kanunu":
        print("✅ Source check passed.")
    else:
        print("❌ Source check failed.")
        if articles:
            print(f"Got source: {articles[0]['metadata'].get('source')}")

if __name__ == "__main__":
    test_legislation_filter()
