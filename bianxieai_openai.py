import asyncio

try:
    from .config import bianxieai_openai_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import bianxieai_openai_Config
    from base_chat import aichat
    import aiorequests

class Bianxieai_openai(aichat):
    headers: dict
    data: dict
    response: str
    usage: dict
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int = 0
    finish_reason: str
    config: bianxieai_openai_Config

    def __init__(self):
        super().__init__()
        self.config = bianxieai_openai_Config()
    
    async def asend(self, msg, gid, uid):
        pass
    
    @property
    def get_response(self):
        return self.response.strip()
    
    @property
    def get_usage(self):
        return self.total_tokens
    