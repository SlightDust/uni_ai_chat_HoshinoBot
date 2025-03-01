import asyncio
import base64,httpx

try:
    from .config import zhipu_Config
    from .config import zhipuV_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import zhipu_Config
    from config import zhipuV_Config
    from base_chat import aichat
    import aiorequests

class Zhipu(aichat):
    config: zhipu_Config
    
    def __init__(self):
        super().__init__()
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
        else: # 多轮对话
            self.payload_messages = messages
        await self.chat_history_limiter()
        self.data = {
            'model': self.config.model,
            'messages': self.payload_messages, 
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

class ZhipuV(aichat):
    '''glm支持图片输入的模型
    '''
    config: zhipuV_Config

    def __init__(self):
        super().__init__()
        self.config = zhipuV_Config()
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
    async def asend(self, txt, image_url, gid, uid):
        # QQ图床的链接输入会报错
        # 也不做系统提示词
        # GLM-4V-Flash 不支持base64编码
        pic_ok, b64 = await url2b64(image_url)
        if not pic_ok:
            self.response = "本地下载图片出错"
            return
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.payload_messages = [
            {
                'role': 'user',
                'content': [
                    {
                        'type':'text',
                        'text': txt
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': b64
                        }
                    }
                ]
            }
        ]
        print(self.payload_messages)
        self.data = {
            'model': self.config.model,
            'messages': self.payload_messages, 
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'user_id': str(uid),
        }
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
        await self.token_cost_record(gid, uid, self.total_tokens, self.config.model)
        return resp_j

async def url2b64(url, timeout=10, b_use_system_proxy=False):
    '''
    将url中的内容转换为base64字符串
    Args:
      url(str): 网址
      timeout(int): 超时时间
      b_use_system_proxy(bool): 是否使用系统代理
    Returns:
      tuple: (是否成功, base64字符串)
    '''
    try:
        async with httpx.AsyncClient(proxies=None, timeout=timeout, trust_env=b_use_system_proxy) as client:
            response = await client.get(url, timeout=timeout)
            if response.status_code == 200:
                is_success = True
                b64str = base64.b64encode(response.content).decode('utf-8')
            else:
                is_success = False
                b64str = None
    except Exception as e:
        is_success = False
        b64str = None
    return is_success, b64str

if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        # zhipu = Zhipu()
        # await zhipu.asend('非对称加密在生活中有哪些常见应用', 112233445566, 123456)
        zhipu = ZhipuV()
        await zhipu.asend('怎么理解这张图',"", 112233445566, 123456)
        print(zhipu.get_response())
        print(zhipu.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())