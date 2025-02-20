import asyncio
import httpx
import json
import configparser
import os 

_current_path = os.path.dirname(__file__)
_previous_path = os.path.abspath(os.path.join(_current_path, os.pardir))

config = configparser.ConfigParser()
config.read(os.path.join(_previous_path, 'config.ini'), encoding='utf-8')
api_key = config.get('deepseek', 'api_key')
url = config.get('deepseek', 'url')
model = config.get('deepseek','model')
# print(api_key, url, model)

headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            # 'Accept': 'text/event-stream',
        }
payload_messages = [
                    {
                        'content': '你好！',
                        'role': 'user'
                    }
                ]

payload_data = {
            'model': model,
            'stream': True,
            'frequency_penalty': 0,
            'max_tokens': 4096,
            'presence_penalty': 0,
            'temperature': 0.9,
            'top_p': 1,
            'response_format': {
                'type': 'text'
            },
            'stop': None,
            'messages': payload_messages
        }

async def fetch_sse_httpx(url: str):
    res_text:str = ""
    usage:dict = {}
    async with httpx.AsyncClient(proxies=None, trust_env=False) as client:
        async with client.stream("POST", url, headers=headers, json=payload_data) as response:
            async for line in response.aiter_lines():
                if line.startswith('data:'):
                    data = line[5:].strip()
                    try:
                        json_data = json.loads(data)
                        print(json_data)
                        if 'content' in json_data['choices'][0]['delta']:
                            res_text += json_data['choices'][0]['delta']['content']
                        else: # DONE前最后一个Event
                            usage = json_data['usage']
                    except json.JSONDecodeError:
                        if data.strip() == "[DONE]":
                            print("Done")
                            break
    print(res_text)
    print(usage)


async def main():
    await fetch_sse_httpx(url)


if __name__ == "__main__":
    asyncio.run(main())