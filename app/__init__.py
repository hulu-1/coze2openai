from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    # 导入路由
    with app.app_context():
        from . import routes

    return app
