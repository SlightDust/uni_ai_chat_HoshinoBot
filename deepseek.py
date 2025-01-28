import asyncio
import requests.exceptions
import json

try:
    from .config import deepseek_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import deepseek_Config
    from base_chat import aichat
    import aiorequests

class Deepseek(aichat):
    config: deepseek_Config

    def __init__(self, reasoner=False):
        self.config = deepseek_Config()
        self.reasoner = reasoner
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    async def asend(self, msg, gid, uid):
        url = self.config.url
        self.data = {
            'model': self.config.model if not self.reasoner else self.config.model_reasoner,
            'stream': self.config.stream,
            'frequency_penalty': self.config.frequency_penalty,
            'max_tokens': self.config.max_tokens,
            'presence_penalty': self.config.presence_penalty,
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'response_format': {
                'type': 'text'
            },
            'stop': None,
            'messages':[
                {
                    'content': msg,
                    'role': 'user'
                }
            ]
        }
        if self.config.system:
            self.data['messages'].insert(0, {'content': self.config.system,'role':'system'})
        try:
            resp = await aiorequests.post(url, headers=self.headers, data=json.dumps(self.data), timeout = 60)
        # timeout
        except (asyncio.TimeoutError, requests.exceptions.ConnectionError):
            self.response = "请求超时，请稍后再试"
            return None
        print("=============begin 原始响应============")
        print(await resp.text)
        print("=============end 原始响应============")
        resp_j = await resp.json()
        resp_code = resp.status_code
        error_code = resp_code
        if error_code != 200:
            error_msg = resp_j['error_msg']
            self.response = f"发生错误:\ncode: {error_code}\n{error_msg}"
            return resp_j
        else:
            # 给回复
            self.response = resp_j['choices'][0]['message']['content']
            self.usage = resp_j['usage']
            await self.token_cost_record_new(gid, uid, self.usage, 'deepseek' if not self.reasoner else 'deepseek_reasoner')
            # 处理可能的finish_reason
            finish_reason = resp_j['choices'][0]['finish_reason']
            if finish_reason == 'stop':
                pass
            elif finish_reason == 'length':
                self.response += "\n\n...输出长度达到了模型上下文长度限制，或达到了 max_tokens 的限制"
            elif finish_reason == 'content_filter':
                self.response += "\n\n...输出内容因触发过滤策略而被过滤。"
            elif finish_reason == 'insufficient_system_resource':
                self.response += "\n\n...系统推理资源不足，生成被打断。"
            return resp_j
        
if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        deepseek = Deepseek(reasoner=True)
        await deepseek.asend('3.9和3.11哪个大？', 112233445566, 123456)
        print(deepseek.get_response())
        print(deepseek.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())