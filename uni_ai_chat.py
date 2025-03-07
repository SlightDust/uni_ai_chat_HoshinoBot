import re
import random
from asyncio import sleep as asleep

from nonebot.command.argfilter.extractors import extract_image_urls

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.config import NICKNAME
from .zhipu import Zhipu
from .zhipu import ZhipuV
from .azure_openai import Azure_openai
from .ernie import Ernie
from .spark import Spark
from .qwen import Qwen, QwenQwQ
from .deepseek import Deepseek
from .base_chat import aichat

from .history_util import *

try:
    from yubao.tools.image_tool import image_draw
except:
    def image_draw(text, do_break=True, line_width=600, font_size=16):
        # 还在测试中
        return text

if type(NICKNAME)!=tuple:
    NICKNAME=[NICKNAME]

def _format_reply_msg(ev, aichet: aichat):
    '''编制回复消息'''
    try:
        pic_b64str = image_draw(aichet.get_response().strip(), do_break=True, line_width=600, font_size=16)
        if "base64://" not in pic_b64str:  # 原文返回
            pic = pic_b64str
        else:  # b64图片
            pic = f'[CQ:image,file={pic_b64str}]'
        reply_message = f"[CQ:reply,id={ev.message_id}]{pic}"
    except:
        reply_message = f"[CQ:reply,id={ev.message_id}]{aichet.get_response()}"
    return reply_message


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
        reply_message = _format_reply_msg(ev, zhipu)
        mid = await bot.send(ev, reply_message)
        mid = mid['message_id']
        try:
            await zhipu.chat_history_record(ev.group_id, ev.user_id, mid, 'zhipu', zhipu.payload_messages, zhipu.get_response())
        except Exception as e:
            sv.logger.error("zhipu记录聊天历史发生错误")
            await bot.send(ev, f"zhipu记录聊天历史发生错误{str(e)}")
    except Exception as err:
        await bot.send(ev, str(err))

@sv.on_prefix('glmv')
async def zhipu_vision_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    image = extract_image_urls(ev.message)
    if len(image) == 0:
        await bot.send(ev, "请在同一条消息内发送文字和图片")
        return
    image = image[0]
    zhipuv = ZhipuV()
    try:
        await zhipuv.asend(text, image, ev.group_id, ev.user_id)
        reply_message = f"[CQ:reply,id={ev.message_id}]{zhipuv.get_response()}"
        await bot.send(ev, reply_message) 
    except Exception as err:
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

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
        await bot.send(ev, str(err))

@sv.on_prefix(('qwq','QwQ'))
async def qwq_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    await bot.send(ev, '正在推理，请耐心等待...')
    qwenqwq = QwenQwQ()
    try:
        await qwenqwq.asend(text, ev.group_id, ev.user_id)
        reply_message = _format_reply_msg(ev, qwenqwq)
        mid = await bot.send(ev, reply_message)
        mid = mid['message_id']
        try:
            await qwenqwq.chat_history_record(ev.group_id, ev.user_id, mid, 'qwq', qwenqwq.payload_messages, qwenqwq.get_response())
        except Exception as e:
            sv.logger.error("qwq 记录聊天历史发生错误")
            await bot.send(ev, f"qwq 记录聊天历史发生错误{e}")
        await asleep(1)
        chain = deepseek_reasoning_chain(ev, qwenqwq)
        try:
            await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
        except:
            await bot.send(ev, f"发送推理过程失败")
    except Exception as err:
        await bot.send(ev, str(err))

@sv.on_prefix(('ds', 'deepseek'))
async def deepseek_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    deepseek = Deepseek()
    try:
        await deepseek.asend(text, ev.group_id, ev.user_id)
        reply_message = _format_reply_msg(ev, deepseek)
        mid = await bot.send(ev, reply_message)
        mid = mid['message_id']
        try:
            await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'ds', deepseek.payload_messages, deepseek.get_response())
        except Exception as e: 
            sv.logger.error("ds记录聊天历史发生错误")
            await bot.send(ev, f"ds记录聊天历史发生错误{e}")
    except Exception as err:
        await bot.send(ev, str(err))


@sv.on_prefix(('dsr', 'deepseekr'))
async def deepseek_reasoner_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    await bot.send(ev, '正在推理，请耐心等待...')
    deepseek = Deepseek(reasoner=True)
    try:
        await deepseek.asend(text, ev.group_id, ev.user_id)
        reply_message = _format_reply_msg(ev, deepseek)
        mid = await bot.send(ev, reply_message)
        mid = mid['message_id']
        try:
            await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'dsr', deepseek.payload_messages, deepseek.get_response())
        except Exception as e:
            sv.logger.error("dsr 记录聊天历史发生错误")
            await bot.send(ev, f"dsr 记录聊天历史发生错误{e}")
        await asleep(1)
        chain = deepseek_reasoning_chain(ev, deepseek)
        if "请稍后再试" not in reply_message:
            try:
                await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
            except:
                await bot.send(ev, f"发送推理过程失败")
    except Exception as err:
        await bot.send(ev, str(err))

def deepseek_reasoning_chain(ev, deepseek):
        chain = [
            {"type": "node",
            "data": {"name": str(NICKNAME[0]),
                    "uin": str(ev.self_id),
                    "content": [
                        {"type": "text", "data": {"text": "下面是推理过程"}},
                        ]
                    }
            },
            {"type": "node",
            "data": {"name": str(NICKNAME[0]),
                    "uin": str(ev.self_id),
                    "content": [
                        {"type": "text", "data": {"text": deepseek.get_reasoning()}},
                        ]
                    }
            },
            {"type": "node",
            "data": {"name": str(NICKNAME[0]),
                    "uin": str(ev.self_id),
                    "content": [
                        {"type": "text", "data": {"text": f"推理消耗tokens：{deepseek.get_usage()}"}}
                        ]
                    }
            }
        ]
        return chain

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
                msg.lstrip("ds")
                messages = his_record['messages']
                messages.append({"role":"user", "content":msg})
                deepseek = Deepseek()
                try:
                    await deepseek.asend("", ev.group_id, ev.user_id, True, messages)
                    # reply_message = f"[CQ:reply,id={ev.message_id}]{deepseek.get_response()}"
                    reply_message = _format_reply_msg(ev, deepseek)
                    mid = await bot.send(ev, reply_message)
                    mid = mid['message_id']
                    try:
                        await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'ds', deepseek.payload_messages, deepseek.get_response())
                    except:
                        sv.logger.error("ds多轮对话记录聊天历史发生错误")
                        await bot.send(ev, f"多轮对话记录聊天历史发生错误，可能无法继续进行多轮对话")
                except Exception as err:
                    await bot.send(ev, str(err))
            elif his_record['service'] == 'zhipu':
                msg.lstrip("zhipu")
                messages = his_record['messages']
                messages.append({"role":"user", "content":msg})
                zhipu = Zhipu()
                try:
                    await zhipu.asend(msg, ev.group_id, ev.user_id, True, messages)
                    # reply_message = f"[CQ:reply,id={ev.message_id}]{zhipu.get_response()}"
                    reply_message = _format_reply_msg(ev, zhipu)
                    mid = await bot.send(ev, reply_message)
                    mid = mid['message_id']
                    try:
                        await zhipu.chat_history_record(ev.group_id, ev.user_id, mid, 'zhipu', zhipu.payload_messages, zhipu.get_response())
                    except:
                        sv.logger.error("zhipu多轮对话记录聊天历史发生错误")
                        await bot.send(ev, f"多轮对话记录聊天历史发生错误，可能无法继续进行多轮对话")
                except Exception as err:
                    await bot.send(ev, str(err))
            elif his_record['service'] == 'dsr':
                msg.lstrip("dsr")
                messages = his_record['messages']
                messages.append({"role":"user", "content":msg})
                await bot.send(ev, '正在推理，请耐心等待...')
                deepseek = Deepseek(reasoner=True)
                try:
                    await deepseek.asend(msg, ev.group_id, ev.user_id, True, messages)
                    # reply_message = f"[CQ:reply,id={ev.message_id}]{deepseek.get_response()}"
                    reply_message = _format_reply_msg(ev, deepseek)
                    mid = await bot.send(ev, reply_message)
                    mid = mid['message_id']
                    try:
                        await deepseek.chat_history_record(ev.group_id, ev.user_id, mid, 'dsr', deepseek.payload_messages, deepseek.get_response())
                    except:
                        sv.logger.error("dsr 多轮对话记录聊天历史发生错误")
                        await bot.send(ev, f"多轮对话记录聊天历史发生错误，可能无法继续进行多轮对话")
                    chain = deepseek_reasoning_chain(ev, deepseek)
                    if "请稍后再试" not in deepseek:
                        try:
                            await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
                        except:
                            await bot.send(ev, f"发送推理过程失败")
                except Exception as err:
                    await bot.send(ev, str(err))
            elif his_record['service'] == 'qwq':
                msg.lstrip("qwq")
                messages = his_record['messages']
                messages.append({"role":"user", "content":msg})
                await bot.send(ev, '正在推理，请耐心等待...')
                qwenqwq = QwenQwQ()
                try:
                    await qwenqwq.asend(msg, ev.group_id, ev.user_id, True, messages)
                    reply_message = _format_reply_msg(ev, qwenqwq)
                    mid = await bot.send(ev, reply_message)
                    mid = mid['message_id']
                    try:
                        await qwenqwq.chat_history_record(ev.group_id, ev.user_id, mid, 'qwq', qwenqwq.payload_messages, qwenqwq.get_response())
                    except:
                        sv.logger.error("qwq 多轮对话记录聊天历史发生错误")
                        await bot.send(ev, f"多轮对话记录聊天历史发生错误，可能无法继续进行多轮对话")
                    chain = deepseek_reasoning_chain(ev, qwenqwq)
                    try:
                        await bot.send_group_forward_msg(group_id=ev.group_id, messages=chain)
                    except:
                        await bot.send(ev, f"发送推理过程失败")
                except Exception as err:
                    await bot.send(ev, str(err))
            else:
                await bot.send(ev, f"{his_record['service']}服务暂不支持多轮对话")
        else: # 没有匹配到历史对话
            pass