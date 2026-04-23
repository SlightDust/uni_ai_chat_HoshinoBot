import asyncio
import requests.exceptions
import json
import httpx

try:
    from .config import openrouter_Config
    from .base_chat import aichat
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import openrouter_Config
    from base_chat import aichat

class Openrouter(aichat):
    config: openrouter_Config

    def __init__(self, reasoner: bool = False, model: str = 'x-ai/grok-4.1-fast'):
        super().__init__()
        self.config = openrouter_Config()
        self.reasoner = reasoner  # 是否开启推理
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
        }
        self.model = model
    
    async def asend(self, msg, gid, uid):
        url = self.config.url
        self.payload_messages = [
            {
                'role': 'user',
                'content': msg
            }
        ]
        if self.config.system:
            self.payload_messages.insert(0, {'role':'system','content': f'{self.config.system}'})
        self.data = {
            "model": self.model,
            "messages": self.payload_messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": self.config.max_tokens,
            "stream": False,
            "reasoning": {"enabled": self.reasoner}
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=self.headers, json=self.data, timeout = 600)
        except (asyncio.TimeoutError, requests.exceptions.ConnectionError):
            self.response = "请求超时，请稍后再试"
            return None
        except httpx.RemoteProtocolError:
            self.response = "对端关闭连接而未发送完整的消息体（不完整的分块读取），请稍后再试"
            return None
        print("=============begin 原始响应============")
        print(resp.text)
        print("=============end 原始响应============")
        if resp.text.strip() == '':
            self.response = "服务器返回了空白响应，请稍后再试。"
            return None
        
        resp_j = resp.json()
        if 'error' in resp_j:
            error_code = resp_j['error']['code']
            error_msg = resp_j['error']['message']
            self.response = f"发生错误:\ncode: {error_code}\n{error_msg}"
            return resp_j
        else:
            self.response = resp_j['choices'][0]['message']['content']
            self.usage = resp_j['usage']
            await self.token_cost_record_new(gid, uid, self.usage, f'openrouter/{self.model}')
            finish_reason = resp_j['choices'][0]['finish_reason']
            if finish_reason == 'stop':
                pass
            elif finish_reason == 'length':
                self.response += "\n\n...输出长度达到了模型上下文长度限制，或达到了 max_tokens 的限制"
            elif finish_reason == 'content_filter':
                self.response += "\n\n...输出内容因触发过滤策略而被过滤。"

if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        openrouter = Openrouter()
        await openrouter.asend('python 怎么让python sum函数返回小数，而不是科学计数法', 112233445566, 123456)
        print(openrouter.get_response())
        print(openrouter.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())