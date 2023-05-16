import os

from aiogram.types import Message
from aiogram import Bot, Dispatcher, executor

from yako.context_manager import ContextManager
from yako.runner import init_runner

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)
runner = init_runner(['./simple_scenario.yml'])
ctx_manager = ContextManager()

@dp.message_handler()
async def run_scenario(message: Message):
    ctx = ctx_manager.get_context(str(message.from_id))
    await runner.run(ctx, message)

 
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)