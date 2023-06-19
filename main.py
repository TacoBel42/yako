import os
from prometheus_client import start_http_server

import yaml
from pydantic import BaseModel
from aiogram.types import Message, ChatType
from aiogram.dispatcher.filters import ChatTypeFilter, Filter, Command, IDFilter
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from builder import build_new_scenario

from yako.context_manager import ContextManager
from yako.runner import NoScenario, init_runner

class BotConfig(BaseModel):
    information_text: str
    operator_link: str
    context_drop_command: str
    admin_user_ids: list[int]
    scenario_dirs: list[str]

def load_bot_config() -> BotConfig:
    with open('./bot.yml', 'r') as f:
        conf = yaml.safe_load(f)
        return BotConfig(**conf)

def dump_bot_config(bc: BotConfig):
    with open('./bot.yml', 'w') as f:
        yaml.dump(bc.dict(), f, allow_unicode=True)

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
bot_conf = load_bot_config()
runner = init_runner(bot_conf.scenario_dirs, ContextManager(_ctxs={}))
# admin_filters = [IDFilter(admin_id) for admin_id in bot_conf.admin_user_ids]
def is_admin(message: Message):
    return message.from_id in bot_conf.admin_user_ids

class CreateSimpleScenario(StatesGroup):
    waiting_for_scenario= State()
        
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=[bot_conf.context_drop_command])
async def drop_context(message: Message):
    runner.expire_user_data(str(message.from_id))
    await bot.send_message(message.chat.id, "Если у вас будет новый вопрос - пишите")
    
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=['operator'])
async def get_operator_link(message: Message):
    await bot.send_message(message.chat.id, bot_conf.operator_link)

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=['help'])
async def get_operator_link(message: Message):
    await bot.send_message(message.chat.id, bot_conf.information_text)
    
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), is_admin, commands=['rebuild'])
async def get_operator_link(message: Message):
    global runner
    runner = init_runner(bot_conf.scenario_dirs, runner.context_manager)
    await bot.send_message(message.chat.id, f"Успешно перезапустили {len(runner.scenarios)} сценариев")

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), is_admin, commands=['build'], state="*")
async def create_simple_scenario(message: Message):
    state = dp.current_state(user=message.from_user.id)
    await bot.send_message(message.chat.id, 
                            "Отправьте название, вопрос и ответ в формате: \n" \
                            "Пример вызова(name): Даты ВКР\n"
                            "Описание(опционально - отступ): Этот сценарий расскажет о датах вкр\n" \
                            "Вопрос: Дат* вкр (без знака вопроса)\n"\
                            "Ответ: Дата вкр не известна")
    await state.set_state(CreateSimpleScenario.waiting_for_scenario.state)
 
@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), state=CreateSimpleScenario.waiting_for_scenario.state)   
async def enter_simple_scenario(message: Message, state: FSMContext):
    text = message.text.split('\n')
    if len(text) < 4:
        await bot.send_message(message.from_id, "Не удалось распарсить вопрос-ответ")
        await state.finish()
        return
    scenario_path = build_new_scenario(name=text[0], desc=text[1], question=text[2], answer='\\n'.join(text[3:]))
    global runner
    runner = init_runner(bot_conf.scenario_dirs, runner.context_manager)
    await state.finish()
    await bot.send_message(message.from_id, "Успешно создали сценарий.")

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), is_admin, commands=['edit_help'])
async def get_operator_link(message: Message):
    text = message.text.split('\n')
    if len(text) != 2:
        await bot.send_message(message.from_id, 'Неверный формат')
        return
    bot_conf.information_text = text[1]
    dump_bot_config(bot_conf)
    await bot.send_message(message.chat.id, "Успешно обновили!")

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE), commands=['scenarios'])
async def get_operator_link(message: Message):
    response = f'Доступен {len(runner.scenarios)} сценарий:\n\n'
    for _, scenario  in runner.scenarios.items():
        response += '• "<b>' + scenario.name + '</b>"' + ' - ' + (scenario.desc or "") + '\n'
    await bot.send_message(message.from_id, response, parse_mode='HTML')
        

@dp.message_handler(ChatTypeFilter(ChatType.PRIVATE))
async def run_scenario(message: Message):
    message.text = message.text.strip()
    try:
        await runner.run(str(message.from_id), message)
    except NoScenario:
        await bot.send_message(message.from_id, 'Не смогли распознать сценарий')

if __name__ == '__main__':
    start_http_server(port=8445)
    executor.start_polling(dp, skip_updates=True)