import sys
import os
import json
import requests

def find_similar_companies(original_domain: str, api_key: str) -> list[str]:
    url = "https://api.ocean.io/v3/search/companies"

    headers = {"X-Api-Token": api_key, "Content-Type": "application/json"}
    
    payload = {
        "size": 2,
        "companiesFilters": {
            "lookalikeDomains": [
                original_domain
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())

    if response.status_code != 200:
        raise Exception(f"Ocean.io API error {response.status_code}: {response.text}")
    
    data = response.json()
    domains = [item["company"]["domain"] for item in data.get("companies", []) if item.get("company", {}).get("domain")]

    return domains

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Write all arguments carefully!!")
        sys.exit(1)

    api_key = os.getenv("OCEAN_API_KEY")
    seed = sys.argv[1]

    try:
        results = find_similar_companies(seed, api_key)
        print(f"Sourced domains: {results}")
        with open("ocean_stage1_output.json", "w") as f:
            json.dump(results, f)

    except Exception as e:
        print(f"Error: {e}")


