import asyncio
import json

try:
    from .config import ernie_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import ernie_Config
    from base_chat import aichat
    import aiorequests

class Ernie(aichat):
    config: ernie_Config
    access_token: str
    is_get_access_token: bool = False
    error_message: str = ""
    need_clear_history: bool = False
    free_mode: bool = True

    def __init__(self):
        self.config = ernie_Config()
        super().__init__()
    
    async def asend(self, msg, gid, uid):
        await self.get_access_token()
        if not self.is_get_access_token:
            self.response = f"获取access_token失败：\n{self.error_message}"
            return False

        if self.config.auth_method == "access_token":
            model = self.config.free_model if self.free_mode else self.config.model
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={self.access_token}"
            self.data = json.dumps({
                "messages":[
                    {
                        "role": "user",
                        "content": msg
                    }
                ],
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "penalty_score": self.config.penalty_score,
                "system": self.config.system,
                "max_output_tokens": self.config.max_output_tokens,
                "user_id": str(uid),
                # 下面两个参数是3.5和4的websearch的返回参考资料标记
                "enable_citation": self.config.enable_citation,
                "enable_trace": self.config.enable_trace
            })
            self.headers = {
                'Content-Type': 'application/json'
            }
            response = await aiorequests.request("POST", url, headers=self.headers, data=self.data)
            resp_j = await response.json()
            print(resp_j)
            if "error_code" in resp_j.keys():
                # 发生错误
                error_code = resp_j['error_code']
                error_message = resp_j['error_msg']
                self.response = f"发生错误:\ncode: {error_code}\n{error_message}"
                return resp_j
            self.response = resp_j['result']
            self.usage = resp_j['usage']
            self.completion_tokens = resp_j['usage']['completion_tokens']
            self.prompt_tokens = resp_j['usage']['prompt_tokens']
            self.total_tokens = resp_j['usage']['total_tokens']

            if resp_j['is_truncated']:
                self.response += "......\n\n输出已被截断，未提供截断原因。"
            
            if resp_j['need_clear_history']:
                self.need_clear_history = True
                self.response += "\n\n警告：输出被标记为存在安全风险，需要清理历史会话，请自行判断。该内容将在60秒后被撤回。"
            
            # 下面两个在ernie-3.5和ernie-4.0中有
            if 'finish_reason' in resp_j and resp_j['finish_reason'] != 'normal':
                self.response += f"......\n\n输出已被截断，原因：{resp_j['finish_reason']}。"

            if 'search_info' in resp_j:
                search_response = "参考资料：\n"
                search_results = resp_j['search_info']['search_results']
                for search_result in search_results:
                    search_response += f"{search_result['index']}. {search_result['title']} ({search_result['url']})\n"
                self.response += f"\n\n{search_response}"

            await self.token_cost_record(gid, uid, self.total_tokens, 'ernie')
            return resp_j


    async def get_access_token(self):
        '''
            用于access_token鉴权方式时，获取access_token
            建议先判断Ernie.is_get_access_token，再使用Ernie.access_token获取access_token
        '''
        url = f"https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials", 
            "client_id": self.config.client_id, 
            "client_secret": self.config.client_secret
            }
        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = await(await aiorequests.request("POST", url, headers=headers, data=payload, params=params)).json()
        try:
            self.access_token = response['access_token']
            self.is_get_access_token = True
        except KeyError:
            self.is_get_access_token = False
            self.error_message = response['error_description']
        return self.access_token


if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        ernie = Ernie()
        ernie.free_mode = False
        if (await ernie.asend('“鲁道夫象征写出了能笑死人的冷笑话”是什么梗', 112233445566, 1)):
            print(ernie.response)
            print('\n')
            print(ernie.total_tokens)
        else:
            print(ernie.error_message)

        # if ernie.is_get_access_token:
        #     print(ernie.access_token)
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())