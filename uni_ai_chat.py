import re
import random
from asyncio import sleep as asleep
from hoshino import Service
from hoshino.typing import CQEvent
from .zhipu import Zhipu
from .azure_openai import Azure_openai
from .ernie import Ernie

sv = Service('uni_ai_chat', enable_on_default=False)

black_word = ['今天我是什么少女', 'ba来一井']  # 如果有不想触发的词可以填在这里

@sv.on_prefix('zhipu')
async def ai_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    zhipu = Zhipu()
    try:
        await zhipu.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, zhipu.get_response())
    except Exception as err:
        await bot.send(ev, err)

@sv.on_prefix('gpt')
async def ai_reply_prefix(bot, ev: CQEvent):
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
async def ai_reply_prefix(bot, ev: CQEvent):
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
async def ai_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    ernie = Ernie()
    ernie.free_mode = False
    try:
        await ernie.asend(text, ev.group_id, ev.user_id)
        await bot.send(ev, ernie.get_response())
    except Exception as err:
        await bot.send(ev, err)