import asyncio

try:
    from .config import zhipu_Config
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

class bianxieai_openai(aichat):
    def __init__(self):
        super().__init__()
    
    async def asend(self, msg, gid, uid):
        pass