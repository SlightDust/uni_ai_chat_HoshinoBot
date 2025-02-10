import re
import random
from asyncio import sleep as asleep
from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.config import NICKNAME
from .zhipu import Zhipu
from .azure_openai import Azure_openai
from .ernie import Ernie
from .spark import Spark
from .qwen import Qwen
from.deepseek import Deepseek

from .history_util import *

if type(NICKNAME)!=tuple:
    NICKNAME=[NICKNAME]

sv = Service('uni_ai_chat', enable_on_default=False)

black_word = ['今天我是什么少女', 'ba来一井']  # 如果有不想触发的词可以填在这里

@sv.on_prefix(('zhipu','glm'))
async def zhipu_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    zhipu = Zhipu()
    try:
        await zhipu.asend(text, ev.group_id, ev.user_id)
        reply_message = f"[CQ:reply,id={ev.message_id}]{zhipu.get_response()}"
        mid = await bot.send(ev, reply_message) 
        mid = mid['message_id']
        await zhipu.chat_history_record(ev.group_id, ev.user_id, mid, 'zhipu', zhipu.payload_messages, zhipu.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('gpt')
async def azureopenai_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    azure_openai = Azure_openai()
    try:
        await azure_openai.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, azure_openai.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('ernie')
async def ernie_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    ernie = Ernie()
    try:
        await ernie.asend(text, ev.group_id, ev.user_id)
        result = await bot.send(ev, ernie.get_response())
        if ernie.need_clear_history:
            try:
                await asleep(60)
                await bot.delete_msg(self_id=ev.self_id, message_id=result['message_id'])
                await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
            except Exception as e:
                await bot.send(ev, f'撤回消息失败，请反馈,{e}')
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('webernie')
async def ernie3_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    ernie = Ernie()
    ernie.free_mode = False
    try:
        await ernie.asend(text, ev.group_id, ev.user_id)
        result = await bot.send(ev, ernie.get_response())
        if ernie.need_clear_history:
            try:
                await asleep(60)
                await bot.delete_msg(self_id=ev.self_id, message_id=result['message_id'])
                await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
            except Exception as e:
                await bot.send(ev, f'撤回消息失败，请反馈,{e}')
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('spark')
async def spark_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    spark = Spark()
    try:
        await spark.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, spark.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('qwenl')
async def qwen_long_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    qwen = Qwen()
    try:
        await qwen.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, qwen.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('qwent')
async def qwen_turbo_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    qwen = Qwen()
    qwen.enable_search = True
    try:
        await qwen.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, qwen.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix(('ds', 'deepseek'))
async def deepseek_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    deepseek = Deepseek()
    try:
        await deepseek.asend(text, ev.group_id, ev.user_id)
        reply_message = f"[CQ:reply,id={ev.message_id}]{deepseek.get_response()}"
        mid = await bot.send(ev, reply_message) 
        mid = mid['message_id']
        await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'ds', deepseek.payload_messages, deepseek.get_response())
    except Exception as err:
        await bot.send(ev, err)


@sv.on_prefix(('dsr', 'deepseekr'))
async def deepseek_reasoner_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    await bot.send(ev, '正在推理，请耐心等待...')
    deepseek = Deepseek(reasoner=True)
    try:
        await deepseek.asend(text, ev.group_id, ev.user_id)
        reply_message = f"[CQ:reply,id={ev.message_id}]{deepseek.get_response()}"
        await bot.send(ev, reply_message)
        await asleep(1)
        chain = [
            {"type": "node",
             "data": {"name": str(NICKNAME[0]),
                      "uin": str(ev.self_id),
                      "content": [
                          {"type": "text", "data": {"text": "下面是推理过程"}},
                          {"type": "text", "data": {"text": deepseek.get_reasoning()}},
                          {"type": "text", "data": {"text": f"推理消耗：{deepseek.get_usage()}"}}
                        ]
                    }
            }
        ]
        if "请稍后再试" not in reply_message:
            await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
    except Exception as err:
        await bot.send(ev, err)

@sv.on_message()
async def ai_chat_continue(bot, ev):
    p1 = re.compile(r'\[CQ:reply,id=(.*?)\]', re.S)  # 匹配规则
    reply_msg_id = re.findall(p1, ev.raw_message)  # 消息id
    if not reply_msg_id:
        return
    reply_msg_id = reply_msg_id[0]
    msg = str(ev.message.extract_plain_text()).strip()
    # sv.logger.info(f"收到对{reply_msg_id}的回复，进行多轮AI对话")
    history = load_history()
    for his_record in history:
        if his_record['mid'] == str(reply_msg_id):
            sv.logger.info(f"收到对{reply_msg_id}的回复，调用{his_record['service']}进行多轮AI对话")
            if his_record['service'] == 'ds':
                messages = his_record['messages']
                messages.append({"role":"user", "content":msg})
                deepseek = Deepseek()
                try:
                    await deepseek.asend("", ev.group_id, ev.user_id, True, messages)
                    reply_message = f"[CQ:reply,id={ev.message_id}]{deepseek.get_response()}"
                    mid = await bot.send(ev, reply_message)
                    mid = mid['message_id']
                    await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'ds', deepseek.payload_messages, deepseek.get_response())
                except Exception as err:
                    await bot.send(ev, err)
            else:
                await bot.send(ev, f"{his_record['service']}服务暂不支持多轮对话")