import os

from pydantic import BaseModel
from aiogram.types import Message, ChatType
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram import Bot, Dispatcher, executor
import yaml

from yako.context_manager import ContextManager
from yako.runner import init_runner

class BotConfig(BaseModel):
    information_text: str
    operator_link: str
    context_drop_command: str

def load_bot_config() -> BotConfig:
    with open('./bot.yml', 'r') as f:
        conf = yaml.safe_load(f)
        return BotConfig(**conf)

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)
runner = init_runner(['./example_scenarios/*.yml'], ContextManager(_ctxs={}))
bot_conf = load_bot_config()
        
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=[bot_conf.context_drop_command])
async def drop_context(message: Message):
    runner.expire_user_data(str(message.from_id))
    await bot.send_message(message.chat.id, "Если у вас будет новый вопрос - пишите")
    
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=['/operator'])
async def get_operator_link(message: Message):
    await bot.send_message(message.chat.id, bot_conf.operator_link)

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=['/help'])
async def get_operator_link(message: Message):
    await bot.send_message(message.chat.id, bot_conf.information_text)

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE))
async def run_scenario(message: Message):
    await runner.run(str(message.from_id), message)

 
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)