import requests
import re

def extract_city_name(text):

    text = text.lower().strip()

    # adding regular expression
    match = re.search(r"about\s+([a-zA-Z ]+)", text)
    if match:
        return match.group(1).strip().title()

    match = re.search(r"in\s+([a-zA-Z ]+)", text)
    if match:
        return match.group(1).strip().title()

    return text.split()[-1].title()


def fetch_api_data(query_text):
    try:
        city_name = extract_city_name(query_text)

        # Normalize format 
        wiki_name = city_name.replace(" ", "_")

        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {"error": f"City not found: {city_name}"}

        data = response.json()

        return {
            "city": city_name,
            "title": data.get("title"),
            "description": data.get("description", "No description available"),
            "summary": data.get("extract", "No summary available"),
        }

    except Exception as e:
        return {"error": str(e)}
