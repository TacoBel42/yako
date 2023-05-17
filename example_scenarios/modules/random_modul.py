from asyncio import sleep
import os
from typing import Any
from aiogram import Bot
from aiogram.types import Message
from random import randint

client = None

async def call(state: dict[str, Any], message: Message):
    rand = randint(state['from'], state['to'])
    await sleep(1)
    await client.send_message(message.from_id, f"И мой ответ...")
    state['answer'] = rand
    return state

def init():
    global client
    client = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))