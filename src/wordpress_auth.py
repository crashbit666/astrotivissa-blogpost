import requests
from config.settings import WORDPRESS_API_URL, WORDPRESS_USERNAME, WORDPRESS_PASSWORD


def get_jwt_token():
    url = f"{WORDPRESS_API_URL.replace('/wp/v2/posts', '/jwt-auth/v1/token')}"
    data = {
        "username": WORDPRESS_USERNAME,
        "password": WORDPRESS_PASSWORD
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["token"]
