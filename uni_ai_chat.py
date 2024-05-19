import re
import random
from hoshino import Service
from hoshino.typing import CQEvent
from .zhipu import Zhipu

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
        await bot.send(ev, zhipu.get_response)
    except Exception as err:
        await bot.send(ev, err)