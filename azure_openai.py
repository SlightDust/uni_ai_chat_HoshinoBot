import asyncio

try:
    from .config import azure_openai_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import azure_openai_Config
    from base_chat import aichat
    import aiorequests

class Azure_openai(aichat):
    finish_reason: str
    config: azure_openai_Config

    def __init__(self):
        super().__init__()
        self.config = azure_openai_Config()
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.config.api_key
        }
        self.config.api_base = f"{self.config.api_end_point}openai/deployments/{self.config.deply_name}/chat/completions?api-version={self.config.api_version}"
        # 容错
        self.config.api_base = self.config.api_base.replace('//', '/')
        self.config.api_base = self.config.api_base.replace('https:/', 'https://')
    
    async def asend(self, msg, gid, uid):
        self.data = {
            'messages': [
                {
                    'role': 'user',
                    'content': msg
                },
            ],
            'max_tokens': self.config.max_tokens,
            # 'temperature': self.config.temperature,
        }
        if self.config.system:
            self.data['messages'].insert(0, {'role':'system','content': f'{self.config.system}'})
        resp = await aiorequests.post(f'{self.config.api_base}', headers=self.headers, json=self.data)
        print((await resp.text))
        resp_j = await resp.json()
        if "error" in resp_j.keys():
            # 发生错误
            error_code = resp_j['error']['code']
            error_message = resp_j['error']['message']
            self.response = f"发生错误:\ncode: {error_code}\n"
            if "rate limit of" in resp_j['error']['message']:
                # 错误原因：速率限制
                self.response += "速率限制，请稍后再试"
            elif "response was filtered" in error_message:
                # 错误原因：内容被过滤
                try:
                    # 尝试读取过滤原因
                    details = ""
                    content_filter_result = resp_j['error']['innererror']['content_filter_result']
                    for key, value in content_filter_result.items():
                        if value['filtered']:
                            details += f"已检测到敏感类型: {key}, 严重性: {value['severity']}。\n"
                    if details == "":
                        details = "未知的过滤原因"
                except Exception as e:
                    # 任何异常
                    details = f"检测过滤原因时出现错误，请回报管理员。\n{e}"
                self.response += f"内容被过滤，请重新输入，尝试读取过滤原因如下:\n{details}"
            else:
                # 其他暂时不知道的错误
                self.response += f"错误信息: {error_message}"
            return resp_j
        # print(resp_j)
        # 无错误
        self.response = resp_j['choices'][0]['message']['content']
        self.prompt_tokens = int(resp_j['usage']['prompt_tokens'])
        self.total_tokens = int(resp_j['usage']['total_tokens'])
        self.finish_reason = resp_j['choices'][0]['finish_reason']
        if self.finish_reason == 'length':
            # 长度原因被截断
            self.response += f"......\n\n对话已被截断，原因：达到最大长度{self.config.max_tokens}tokens。"
        elif self.finish_reason == 'content_filter':
            # 极罕见
            self.response += f"......\n\n对话已被截断，原因：内容过滤。"
        else:
            # self.finish_reason == 'stop' 正常结束
            pass

        await self.token_cost_record(gid, uid, self.total_tokens, 'azure_openai')
        return resp_j

if __name__ == '__main__':

    async def task1():
        print("Task 1 is running")
        aopenai = Azure_openai()
        await aopenai.asend('请介绍一下日本赛马东海帝皇', 112233445566, 1)
        print(aopenai.get_response())
        print(aopenai.get_usage())
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())