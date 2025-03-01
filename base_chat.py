import json
import os

try:
    from .config import global_Config
except ImportError:
    import sys
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import global_Config

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
        self.global_config = global_Config()
        self.history_limit = self.global_config.history_limit
        assert isinstance(self.history_limit, int), 'history_limit must be an integer'
        assert self.history_limit > 0, 'history_limit must be greater than 0'
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
    
    async def chat_history_limiter(self, limit=None):
        '''预处理，限制携带的历史对话轮数
        Args:
            limit (int): 限制轮数
        Returns:
            list: 携带的历史对话。同时也会直接修改self.payload_messages
        '''
        if limit is None:
            limit = self.history_limit
        messages = []
        if len(messages) <= limit:
            return self.payload_messages
        
        if self.payload_messages[0]['role'] == 'system':
            messages[0] = self.payload_messages[0]  # 这个是systemn
        else:
            messages = self.payload_messages[-limit*2-1:]  # 携带最近limit轮和最后一次用户输入
            self.payload_messages = messages
            return messages

    def get_response(self):
        '''获取AI响应'''
        return self.response.strip()
    
    def get_usage(self):
        '''获取本次调用消耗的总tokens'''
        return self.total_tokens

if __name__ == '__main__':
    a = aichat()
    a.token_cost_record(123456, 123456789, 100, 'api')