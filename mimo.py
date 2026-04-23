import asyncio
import requests.exceptions
import json
import httpx

try:
    from .config import mimo_Config
    from .base_chat import aichat
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import mimo_Config
    from base_chat import aichat

class mimo(aichat):
    def __init__(self):
        super().__init__()
        self.config = mimo_Config()
        self.thinking = self.config.reasoner
        self.model = self.config.model
        self.headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
        }

    async def asend(self, msg, gid, uid, continue_flag:bool=False, messages:list=None):
        '''
        continue_flag: 是否为多轮对话
        messages: 已经拼接好的多轮对话的历史消息，0是system，-1是最后一个用户输入，中间是多轮对话
        '''
        url = self.config.url
        if not continue_flag:
            self.payload_messages = [
                    {
                        'content': msg,
                        'role': 'user'
                    }
                ]
            self.payload_messages.insert(0, {'content': self.config.system,'role':'system'})
        else: # 多轮对话
            self.payload_messages = messages
        await self.chat_history_limiter()

        self.data = {
            "model": self.model,
            "messages": self.payload_messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_completion_tokens": self.config.max_tokens,
            "stream": False,
            'thinking': {"type": "disabled" if not self.thinking else "enabled"}
        }
        if self.config.use_web_search:
            self.data.update({"tools":[{"type":"web_search"}]})

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=self.headers, json=self.data, timeout = 600)
        except (asyncio.TimeoutError, requests.exceptions.ConnectionError):
            self.response = "请求超时，请稍后再试"
            return None
        except httpx.RemoteProtocolError:
            self.response = "对端关闭连接而未发送完整的消息体（不完整的分块读取），请稍后再试"
            return None
        except httpx.ConnectError:
            self.response = "连接失败，请稍后再试"
            return None
        print("=============begin 原始响应============")
        print(resp.text)
        print("=============end 原始响应============")
        if resp.text.strip() == '':
            self.response = "服务器返回了空白响应，请稍后再试。"
            return None
        
        resp_j = resp.json()
        if 'error' in resp_j:
            try:
                error_code = resp_j['error']['code']
                error_msg = resp_j['error'].get('message',"")
                error_msg += "\n" + resp_j['error'].get('param', "")
                self.response = f"发生错误:\ncode: {error_code}\n{error_msg}"
            except:
                error_msg = f"发生错误但解析失败，原始返回信息{resp.text}"
            return resp_j
        else:
            self.response = resp_j['choices'][0]['message']['content']
            self.usage = resp_j['usage']
            await self.token_cost_record_new(gid, uid, self.usage, f'Xiaomi/{self.model}')
            finish_reason = resp_j['choices'][0]['finish_reason']
            if finish_reason == 'stop':
                pass
            elif finish_reason == 'length':
                self.response += "\n\n...输出长度达到了模型上下文长度限制，或达到了 max_tokens 的限制"
            elif finish_reason == 'content_filter':
                self.response += "\n\n...输出内容因触发过滤策略而被过滤。"
            elif finish_reason == 'repetition_truncation':
                self.response += "\n\n...输出内容模型检测到了复读而被截断。"

if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        ai = mimo()
        await ai.asend('python 怎么让python sum函数返回小数，而不是科学计数法', 112233445566, 123456)
        print(ai.get_response())
        print(ai.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())