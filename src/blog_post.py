import requests
from config.settings import WORDPRESS_API_URL, JWT_TOKEN


def create_blog_post(title, thumbnail, video_url, content, category_id):
    url = WORDPRESS_API_URL
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }

    # Use shortcodes to create a Divi layout
    divi_content = f"""
    [et_pb_section bb_built="1" _builder_version="4.9.10" background_color="transparent"]
        [et_pb_row]
            [et_pb_column type="4_4"]
                [et_pb_text _builder_version="4.9.10" text_orientation="center" text_text_color="#ffffff"]
                    <h1 style="color: #ffffff;">{title}</h1>
                [/et_pb_text]
                [et_pb_image src="{thumbnail}" _builder_version="4.9.10" _module_preset="default" _module_preset_name="Image" _module_preset_type="default" align="center" url="{video_url}" url_new_window="on"]
                [/et_pb_image]
                [et_pb_text _builder_version="4.9.10" text_text_color="#ffffff"]
                    {content}
                [/et_pb_text]
            [/et_pb_column]
        [/et_pb_row]
    [/et_pb_section]
    """

    data = {
        "title": title,
        "content": divi_content,
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
