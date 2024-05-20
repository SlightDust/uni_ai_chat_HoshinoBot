import json
import os

current_path = os.path.dirname(__file__)
token_cost_path = os.path.join(current_path, 'token_cost.json')
if not os.path.exists(token_cost_path):
    with open(token_cost_path, 'w', encoding='utf-8') as f:
        f.write('{}')

class aichat:
    def __init__(self):
        pass
    async def token_cost_record(self, gid, uid, cost, api):
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

if __name__ == '__main__':
    a = aichat()
    a.token_cost_record(123456, 123456789, 100, 'api')