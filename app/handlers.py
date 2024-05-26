import logging

import requests
import json
import time
from flask import Response, jsonify
from .utils import handle_error
from .utils import is_dict_list, upload_image_to_telegraph, generate_error_response


def handle_stream_response(coze_api_url, headers, request_body, model):
    try:
        with requests.post(coze_api_url, headers=headers, json=request_body) as r:
            if 'text/event-stream' not in r.headers.get('Content-Type'):
                return process_un_stream_response(r, model)
            else:
                return Response(generate(r, model), content_type='text/event-stream')
    except Exception as e:
        return handle_error(e)


def handle_un_stream_response(coze_api_url, headers, request_body, model):
    try:
        response = requests.post(coze_api_url, headers=headers, json=request_body)
        return process_un_stream_response(response, model)
    except Exception as e:
        return handle_error(e)


def generate(r, model):
    buffer = b""
    for chunk in r.iter_content(chunk_size=10):
        buffer += chunk
        while b'\n\n' in buffer:
            line, buffer = buffer.split(b'\n\n', 1)
            yield from process_line(line.decode('utf-8').strip(), model)

    if buffer:
        yield from process_line(buffer.decode('utf-8').strip(), model)


def process_un_stream_response(response, model):
    response_data = response.json()
    # logging.info(f"Response from Coze API: {response_data}")
    if response_data.get('code') == 0 and response_data.get('msg') == 'success':
        messages = response_data.get('messages', [])
        answer_message = next((msg for msg in messages if msg['role'] == 'assistant' and msg['type'] == 'answer'), None)

        if answer_message:
            result = answer_message['content'].strip()
            usage_data = {
                "prompt_tokens": 100,
                "completion_tokens": 10,
                "total_tokens": 110
            }
            chunk_id = f"chatcmpl-{int(time.time())}"
            chunk_created = int(time.time())

            formatted_response = {
                "id": chunk_id,
                "object": "chat.completion",
                "created": chunk_created,
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result
                    },
                    "logprobs": None,
                    "finish_reason": "stop"
                }],
                "usage": usage_data,
                "system_fingerprint": "fp_2f57f81c11"
            }
            return jsonify(formatted_response)
        else:
            return jsonify({"error": "No answer message found."}), 500
    else:
        return generate_error_response("Unexpected response from Coze API." + response_data.get('msg'), response_data.get('code'))


def process_line(line, model):
    if not line.startswith("data:"):
        return

    try:
        chunk_obj = json.loads(line[5:])
    except json.JSONDecodeError:
        return

    event = chunk_obj.get("event")
    message = chunk_obj.get("message", {})
    response = generate_response(event, message, model)
    if response:
        yield response
        if event in ["done", "error"]:
            return


def generate_response(event, message, model):
    timestamp = int(time.time())

    if event == "message" and message["role"] == "assistant" and message["type"] == "answer":
        content = message.get("content", "")
        response_data = {
            "id": f'chatcmpl-{timestamp}',
            "object": "chat.completion.chunk",
            "created": timestamp,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": content, "role": "assistant"},
                "finish_reason": None
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": len(content), "total_tokens": len(content)},
            "system_fingerprint": None
        }
        return f"data: {json.dumps(response_data)}\n\n"
    elif event in ["done", "error"]:
        response_data = {
            "id": f'chatcmpl-{timestamp}',
            "object": "chat.completion.chunk",
            "created": timestamp,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": 'stop'
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "system_fingerprint": None
        }
        return f"data: {json.dumps(response_data)}\n\n"

def handle_last_message(last_message):
    last_message_content = last_message.get("content")
    if is_dict_list(last_message_content):
        texts = []
        image_urls = []
        for item in last_message_content:
            if item.get("type") == "text":
                texts.append(item.get("text", ""))
            elif item.get("type") == "image_url":
                image_urls.append(item.get("image_url", {}).get("url", ""))
        # Check for base64 encoded image data
        for image_url in image_urls:
            if image_url.startswith('data:image'):
                # Call upload_image_to_telegraph and get the returned URL
                uploaded_image_url = upload_image_to_telegraph(image_url)
                texts.append(uploaded_image_url)
        query_string = ",".join(texts)
    else:
        query_string = str(last_message.get("content", ""))
    return query_string


def handle_last_message_v2(last_message):
    last_message_content = last_message.get("content")

    output = {"item_list": []}

    if is_dict_list(last_message_content):
        texts = []
        image_urls = []
        for item in last_message_content:
            if item.get("type") == "text":
                output["item_list"].append({
                    "type": "text",
                    "text": item["text"]
                })
            elif item.get("type") == "image_url":
                image = item.get("image_url", {}).get("url", "")
                if image.startswith('data:image'):
                    image = upload_image_to_telegraph(image)
                output["item_list"].append({
                    "type": "image",
                    "image": {
                        # "key": "1234567",
                        "image_thumb": {
                            "url":image,
                        },
                        "image_ori": {
                            "url": image,
                        },
                        "feedback": None
                    }
                })
                image_urls.append(image)
        # Check for base64 encoded image data
        for image_url in image_urls:
            if image_url.startswith('data:image'):
                # Call upload_image_to_telegraph and get the returned URL
                uploaded_image_url = upload_image_to_telegraph(image_url)
                texts.append(uploaded_image_url)
        query_string = str(output)
    else:
        query_string = str(last_message.get("content", ""))
    return query_string
