import json
import os

current_path = os.path.dirname(__file__)
token_cost_path = os.path.join(current_path, 'token_cost.json')
if not os.path.exists(token_cost_path):
    with open(token_cost_path, 'w', encoding='utf-8') as f:
        f.write('{}')

class aichat:
    headers: dict  # 请求头
    data: dict     # 请求数据
    response: str  # 响应数据
    usage: dict    # 消耗tokens，包含下面三个
    completion_tokens: int   # 补全tokens
    prompt_tokens: int       # 提示词tokens
    total_tokens: int = 0    # 总tokens
    def __init__(self):
        pass

    async def asend(self, msg, gid, uid) -> dict:
        '''异步，向AI提问'''
        pass

    async def token_cost_record(self, gid, uid, cost, api):
        '''记录token消耗
        Args:
            gid (int): 群号
            uid (int): 用户号（QQ号）
            cost (int): 消耗的tokens数
            api (str): 调用的api名称
        '''
        gid = str(gid)
        uid = str(uid)
        with open(token_cost_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if gid not in data:
            data[gid] = {}
        if api not in data[gid]:
            data[gid][api] = {}
        if uid not in data[gid][api]:
            data[gid][api][uid] = 0
        data[gid][api][uid] += cost
        data[gid][api]['total'] = sum(value for key, value in data[gid][api].items() if key != 'total')
        with open(token_cost_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_response(self):
        '''获取AI响应'''
        return self.response
    
    def get_usage(self):
        '''获取本次调用消耗的总tokens'''
        return self.total_tokens

if __name__ == '__main__':
    a = aichat()
    a.token_cost_record(123456, 123456789, 100, 'api')