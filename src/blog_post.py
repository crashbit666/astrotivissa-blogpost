import requests
from config.settings import WORDPRESS_API_URL, JWT_TOKEN


def create_blog_post(title, content, category_id):
    url = WORDPRESS_API_URL
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "content": f'<div style="background-color: #191919; color: #ffffff; padding: 20px;">{content}</div>',
        "categories": [category_id],
        "status": "publish"
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Failed to create blog post: {e}")
        print(f"Response content: {response.content}")
        raise
    return response.json()
