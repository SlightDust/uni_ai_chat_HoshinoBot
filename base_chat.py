import json
import os

current_path = os.path.dirname(__file__)
token_cost_path = os.path.join(current_path, 'token_cost.json')
chat_history_path = os.path.join(current_path, 'chat_history.json')

if not os.path.exists(token_cost_path):
    with open(token_cost_path, 'w', encoding='utf-8') as f:
        f.write('{}')

if not os.path.exists(chat_history_path):
    with open(chat_history_path, 'w', encoding='utf-8') as f:
        f.write('[]')

class aichat:
    headers: dict  # 请求头
    data: dict     # 请求数据
    response: str  # 响应数据
    usage: dict    # 消耗tokens，包含下面三个
    completion_tokens: int   # 补全tokens
    prompt_tokens: int       # 提示词tokens
    total_tokens: int = 0    # 总tokens
    payload_messages: list  # 对话列表
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

    async def token_cost_record_new(self, gid, uid, usage, api):
        '''直接传入usage数组，记录token消耗
        Args:
            usage (dict): api返回的usage数组
            api (str): 调用的api名称
        '''
        gid = str(gid)
        uid = str(uid)
        try:
            cost = int(usage['total_tokens'])
        except:
            cost = int(usage['completion_tokens']) + int(usage['prompt_tokens'])
        self.total_tokens = cost
        await self.token_cost_record(gid, uid, cost, api)

    async def chat_history_record(self, gid, uid, mid, service, messages, assistant_reply):
        '''记录ai对话历史
        Args:
            gid (int): 群号
            uid (int): QQ号
            mid (int): 消息id
            service (str): 服务名称
            messages (list): 消息列表
            assistant_reply (str): ai回复
        '''
        gid = str(gid)
        uid = str(uid)
        mid = str(mid)
        messages.append({'role':'assistant','content':assistant_reply})
        with open(chat_history_path, 'r', encoding='utf-8') as f:
            whold_data = json.load(f)
        new_data = {
            'gid': gid,
            'uid': uid,
            'mid': mid,
            'service': service,
            'messages': messages
        }
        whold_data.append(new_data)
        with open(chat_history_path, 'w', encoding='utf-8') as f:
            json.dump(whold_data, f, ensure_ascii=False, indent=4)

    def get_response(self):
        '''获取AI响应'''
        return self.response.strip()
    
    def get_usage(self):
        '''获取本次调用消耗的总tokens'''
        return self.total_tokens

if __name__ == '__main__':
    a = aichat()
    a.token_cost_record(123456, 123456789, 100, 'api')