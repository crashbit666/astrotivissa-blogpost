import requests
from config.settings import WORDPRESS_API_URL


def get_jwt_token(username, password):
    url = f"{WORDPRESS_API_URL.replace('/wp/v2/posts', '/jwt-auth/v1/token')}"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["token"]
