import requests


def get_location_by_ip(ip: str):
    response = requests.get(f"https://ipapi.co/{ip}/json/").json()

    location_data = {
        "ip": response.get("ip"),
        "version": response.get("version"),
        "city": response.get("city"),
        "region": response.get("region"),
        "region_code": response.get("region_code"),
        "country": response.get("country"),
        "country_code": response.get("country_code"),
        "country_code_iso3": response.get("country_code_iso3"),
        "country_name": response.get("country_name"),
        "latitude": response.get("latitude"),
        "longitude": response.get("longitude"),
        "timezone": response.get("timezone"),
    }

    return location_data
