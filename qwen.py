try:
    from .config import qwen_Config
    from .base_chat import aichat
    import httpx, json
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import qwen_Config
    from base_chat import aichat
    import httpx, json
    import aiorequests

class Qwen(aichat):
    config: qwen_Config
    enable_search: bool = False
    def __init__(self):
        super().__init__()
        self.config = qwen_Config()
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
        }

    async def asend(self, msg, gid, uid):
        url = self.config.url
        self.data = {
            "model": self.config.model,
            "messages": [
                {
                    'role': 'user',
                    'content': msg
                },
            ],
            "top_p": self.config.top_p,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False,
        }
        if self.config.system:
            self.data['messages'].insert(0, {'role':'system','content': f'{self.config.system}'})
        if self.enable_search:
            self.data['model'] = self.config.model_search
            self.data['enable_search'] = True
        # print(self.data)
        resp = await aiorequests.post(f'{url}', headers=self.headers, json=self.data)
        resp_j = await resp.json()
        print(resp_j)
        if "error" in resp_j.keys():
            # 发生错误
            error_code = resp_j['error']['code']
            error_message = resp_j['error']['message']
            self.response = f"发生错误:\ncode: {error_code}\n{error_message}"
            return resp_j
        self.response = resp_j['choices'][0]['message']['content']
        self.usage = resp_j['usage']
        self.completion_tokens = int(resp_j['usage']['completion_tokens'])
        self.prompt_tokens = int(resp_j['usage']['prompt_tokens'])
        self.total_tokens = int(resp_j['usage']['total_tokens'])
        # model很有辨识度，所以就拿model名字来分别记了
        await self.token_cost_record(gid, uid, self.total_tokens, self.data['model'])
        return resp_j
        
class QwenQwQ(aichat):
    config: qwen_Config
    def __init__(self):
        super().__init__()
        self.config = qwen_Config()
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def asend(self, msg, gid, uid, continue_flag=False, message:list=None):
        if not continue_flag:
            self.payload_messages = [
                {
                    "role": "user",
                    "content": msg
                }
            ]
        else:  #多轮对话
            self.payload_messages = message
        await self.chat_history_limiter(10)
        self.data = {
            "model": self.config.model_QwQ,
            "stream": True,
            "stream_options": {
                "include_usage": True
            },
            "messages": self.payload_messages,
        }
        try:
            async with httpx.AsyncClient(proxies=None, trust_env=False) as client:
                async with client.stream("POST", self.config.url, headers=self.headers, json=self.data) as sse_response:
                    await self.openai_like_sse_process(sse_response)
        except Exception as e:
            print(f"Error: {str(e)}")
            self.response = f"发送请求或解析SSE时发生错误{str(e)}"
            return
        await self.token_cost_record_new(gid, uid, self.usage, self.data['model'])

if __name__ == '__main__':
    import asyncio
    async def task1():
        print("Task 1 is running")
        qwen = QwenQwQ()
        qwen.enable_search = False
        await qwen.asend('3.9和3.11哪个大', 112233445566, 1)
        print(qwen.get_response())
        print(qwen.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())