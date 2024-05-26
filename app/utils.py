import base64
import imghdr
import logging
import traceback

import requests
from flask import request, jsonify


def get_auth_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    return auth_header.split(" ")[1]


def handle_error(e):
    error_response = {
        "error": {
            "message": str(e),
            "type": "coze_2_api_error"
        }
    }
    return jsonify(error_response), 500


def generate_error_response(message, status_code):
    error_response = {
        "error": {
            "message": str(message),
            "type": "coze_api_error"
        }
    }
    return jsonify(error_response), 500


def upload_image_to_telegraph(base64_string):
    try:
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        image_data = base64.b64decode(base64_string)

        image_type = imghdr.what(None, image_data)
        if image_type is None:
            raise ValueError("Invalid image data")

        mime_type = f"image/{image_type}"
        files = {'file': (f'image.{image_type}', image_data, mime_type)}
        response = requests.post('https://telegra.ph/upload', files=files)

        response.raise_for_status()
        json_response = response.json()
        if isinstance(json_response, list) and 'src' in json_response[0]:
            return 'https://telegra.ph' + json_response[0]['src']
        else:
            raise ValueError(f"Unexpected response format: {json_response}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to upload image. Error: {e}")
    except Exception as e:
        raise Exception(f"Failed to upload image. An error occurred: {e}")


def is_dict_list(obj):
    if not isinstance(obj, list):
        return False
    for element in obj:
        if not isinstance(element, dict):
            return False
    return True
