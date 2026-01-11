import requests

def fetch_api_data(city_name):
    try:
        city_name = city_name.strip().title()
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{city_name}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": "City not found"}

        data = response.json()

        return {
            "title": data.get("title"),
            "description": data.get("description", "No description available"),
            "summary": data.get("extract", "No summary available"),
        }

    except Exception as e:
        return {"error": str(e)}
