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
    from config import zhipu_Config
    from base_chat import aichat
    import aiorequests

class Zhipu(aichat):
    config: zhipu_Config
    
    def __init__(self):
        self.config = zhipu_Config()
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
    async def asend(self, msg, gid, uid, continue_flag:bool=False, messages:list=None):
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        if not continue_flag:
            self.payload_messages = [
                    {
                        'role': 'user',
                        'content': msg
                    },
                ]
            if self.config.system:
                self.payload_messages.insert(0, {'role':'system','content': f'{self.config.system}'})
            self.data = {
                'model': self.config.model,
                'messages': self.payload_messages, 
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'top_p': self.config.top_p,
                'user_id': str(uid),
            }
        else: # 多轮对话
            self.payload_messages = messages
            self.data = {
                'model': self.config.model,
                'messages': payload_messages, 
                'max_tokens': self.config.max_tokens,
                'temperature': self.config.temperature,
                'top_p': self.config.top_p,
                'user_id': str(uid),
            }

        if self.config.use_web_search:
            self.data['tools'] = [{'type':'web_search','web_search':{'enable': True, "search_result": True}}]
        resp = await aiorequests.post(f'{url}', headers=self.headers, json=self.data)
        resp_j = await resp.json()
        print(resp_j)
        if "error" in resp_j.keys():
            # 发生错误
            # 智谱的错误信息是汉语，就不画蛇添足了，直接返回。https://open.bigmodel.cn/dev/api#error-code-v3
            error_code = resp_j['error']['code']
            error_message = resp_j['error']['message']
            self.response = f"发生错误:\ncode: {error_code}\n{error_message}"
            return resp_j
        self.response = resp_j['choices'][0]['message']['content']
        self.usage = resp_j['usage']
        self.completion_tokens = int(resp_j['usage']['completion_tokens'])
        self.prompt_tokens = int(resp_j['usage']['prompt_tokens'])
        self.total_tokens = int(resp_j['usage']['total_tokens'])
        await self.token_cost_record(gid, uid, self.total_tokens, 'zhipu')
        return resp_j

if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        zhipu = Zhipu()
        await zhipu.asend('非对称加密在生活中有哪些常见应用', 112233445566, 123456)
        print(zhipu.get_response())
        print(zhipu.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())