import asyncio
import websockets
import base64
import json
import hmac
import hashlib
from urllib.parse import urlparse
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from urllib.parse import urlencode
from websockets.exceptions import InvalidStatusCode, ConnectionClosedError

try:
    from .config import spark_Config
    from .base_chat import aichat
    from hoshino import aiorequests
except ImportError:
    import sys, os
    _current_dir = os.path.dirname(__file__)
    if _current_dir not in sys.path:
        sys.path.insert(0, _current_dir)
    from config import spark_Config
    from base_chat import aichat
    import aiorequests

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, gpt_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

class Spark(aichat):
    config: spark_Config
    def __init__(self):
        self.config = spark_Config()
        super().__init__()
    
    def gen_params(self, uid, query):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": self.config.appid,
                "uid": str(uid),           
                # "patch_id": []    #接入微调模型，对应服务发布后的resourceid          
            },
            "parameter": {
                "chat": {
                    "domain": self.config.domain,
                    "temperature": 0.5,
                    "max_tokens": 4096,
                    "auditing": "default",
                }
            },
            "payload": {
                "message": {
                    "text": [{"role": "user", "content": query}]
                }
            }
        }
        return data

    async def asend(self, msg, gid, uid):
        wsParam = Ws_Param(self.config.appid, self.config.api_key, self.config.api_secret, self.config.url)
        uri = wsParam.create_url()
        data = json.dumps(self.gen_params(uid=uid,query=msg))
        self.response = ""
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(data)
                while True:
                    res = await ws.recv()
                    # print(f"Received: {res}")
                    res = json.loads(res)
                    res_code = res['header']['code']
                    if res_code == 0:
                        # 无错误
                        self.response += res['payload']['choices']['text'][0]['content']
                        if res['header']['status'] == 2:
                            # 流式响应结束标记
                            self.usage = res["payload"]["usage"]["text"]
                            self.completion_tokens = res["payload"]["usage"]["text"]["completion_tokens"]
                            self.prompt_tokens = res["payload"]["usage"]["text"]["prompt_tokens"]
                            self.total_tokens = res["payload"]["usage"]["text"]["total_tokens"]
                            await self.token_cost_record(gid, uid, self.total_tokens, "spark")
                            break
                        else:
                            # 未结束，继续接收报文
                            continue
                    elif res_code == 10013:
                        # 输入违规
                        self.response = "发生错误：输入内容审核不通过，涉嫌违规，请重新调整输入内容"
                        break
                    elif res_code == 10014:
                        # 输出违规
                        self.response += "......\n发生错误: 输出内容涉及敏感信息，审核不通过，后续结果无法展示"
                        break
                    else:
                        # 其他错误
                        self.response = f"发生错误：\ncode: {res['header']['code']}\n{res['header']['message']}"
                        break
        except InvalidStatusCode as err:
            if "HTTP 401" in err:
                self.response = "鉴权失败，请检查APIKey和APISecret是否正确"
        except Exception as err:
            self.response = f"未知错误：{err}"

if __name__ == '__main__':
    async def task1():
        print("Task 1 is running")
        spark = Spark()
        await spark.asend('“鲁道夫象征写出了能笑死人的冷笑话”是什么梗', 112233445566, 1)
        print(spark.response)
        print('\n')
        print(spark.total_tokens)

        # if ernie.is_get_access_token:
        #     print(ernie.access_token)
        print("Task 1 completed")

    async def main():
        # tasks = [task1(), task2()]
        tasks = [task1()]
        await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())