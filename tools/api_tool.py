import requests

BASE_URL = "https://api.api-ninjas.com/v1/city?name="

def fetch_api_data(city_name):
    url = BASE_URL + city_name
    try:
        response = requests.get(url)

        if response.status_code!= 200:
            return f"Error: {response.status_code}, {response.text}"
        data = response.json()
    
        if len(data) == 0:
            return f"No data found for city: {city_name}"
        
        return data[0]
    
    except Exception as error:
        print("Error while calling API:", error)
        return None