import os
import json


class Config:
    COZE_API_BASE = os.getenv("COZE_API_BASE", "api.coze.com")
    DEFAULT_BOT_ID = os.getenv("BOT_ID", "")
    BOT_CONFIG = json.loads(os.getenv("BOT_CONFIG", "{}"))