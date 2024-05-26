import logging

from flask import request, jsonify, Response, g, current_app as app

from .handlers import handle_stream_response, handle_un_stream_response, handle_last_message_v2
from .utils import get_auth_token, handle_error

logging.basicConfig(level=logging.DEBUG)


@app.before_request
def before_request():
    g.data = request.get_json(silent=True)


@app.route('/', methods=['GET'])
def index():
    return '''
        <html>
            <head>
                <title>Coze2OpenAI</title>
            </head>
            <body>
                <h1>Coze2OpenAI</h1>
                <p>DONE.</p>
            </body>
        </html>
    '''


@app.route('/v1/chat/completions', methods=['GET', 'POST', 'OPTIONS'])
def chat_completions():
    if request.method == "OPTIONS":
        return Response(status=204)

    token = get_auth_token()
    if not token:
        return jsonify({'code': 401, 'errmsg': 'Unauthorized.'}), 401

    try:
        data = g.data
        messages = data.get("messages", [])
        model = data.get("model")
        chat_history = [{"role": message["role"], "content": message["content"], "content_type": "text"} for message in messages[:-1] if message["role"] == "assistant"]
        last_message = messages[-1]
        query_string = handle_last_message_v2(last_message)
        # logging.info(f"Query string: {query_string}")
        stream = data.get("stream", False)
        bot_id = app.config.get("BOT_CONFIG", {}).get(model, app.config.get("DEFAULT_BOT_ID", ""))

        request_body = {
            "query": query_string,
            "stream": stream,
            "conversation_id": "",
            "user": "apiuser",
            "bot_id": bot_id,
            # "chat_history": chat_history,
            "draft_mode": True
        }

        coze_api_url = f"https://{app.config['COZE_API_BASE']}/open_api/v2/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        logging.info(f"Request to Coze API: {coze_api_url}")
        logging.info(f"Request bot id : {bot_id}")
        logging.info(f"Request body: {request_body}")

        if stream:
            return handle_stream_response(coze_api_url, headers, request_body, model)
        else:
            return handle_un_stream_response(coze_api_url, headers, request_body, model)
    except Exception as e:
        return handle_error(e)
