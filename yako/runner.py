import glob
import logging 
from aiogram import Bot
from pydantic import BaseModel
from aiogram.types import Message
from prometheus_client import Counter

from yako.exceptions import NoNextNode
from yako.parser import parse_scenario
from yako.scenario import Context, Scenario
from yako.context_manager import IContextManager

scenarios_recognizion_counter = Counter('scenarios_recognizion', 'Распознанование сценариев', ['status'])
scenarios_call_counter = Counter('scenarios_call', 'Выполнение сценариев', ['name'])

logging.basicConfig(
    # filename='./logs/out.log',
    #                 filemode='a',
    #                 format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                 datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger()

class NoScenario(Exception):
    pass

class ScenarioRunnner(BaseModel):
    scenarios: dict[str, Scenario]
    context_manager: IContextManager
    
    async def run(self, identity_id: str, current_message: Message):
        ctx = self.context_manager.get_context(identity_id)
        
        suitable_scenario = None
        ctx.current_message = current_message
        if ctx.current_scenario:
            suitable_scenario = self.scenarios[ctx.current_scenario]
        if not ctx.current_scenario:
            for scenario_name, scenario in self.scenarios.items():
                if scenario.is_suitable(current_message):
                    ctx.current_scenario = scenario_name
                    suitable_scenario = scenario
                    break
        if not suitable_scenario:
            logger.info(f'cant find suitable scenario. request: {current_message.text}')
            scenarios_recognizion_counter.labels(status='false').inc()
            raise NoScenario 
        scenarios_recognizion_counter.labels(status='true').inc()
        if not ctx.modules and suitable_scenario.scenario_modules:
            ctx.modules = suitable_scenario.scenario_modules # make clean
        
        try:
            scenarios_call_counter.labels(name=suitable_scenario.name).inc()
            await suitable_scenario.run(ctx)
        except NoNextNode:
            self.expire_user_data(identity_id)
        except Exception as e:
            logger.error(f'got error during execution: {e}\n scenario: {suitable_scenario.name}')
            self.expire_user_data(identity_id)
            raise e

    
    def add_scenario(self, scenario: Scenario):
        self.scenarios[scenario.name] = scenario
        
    def expire_user_data(self, identity_id: str):
        self.context_manager.drop_context(identity_id)
        
def init_runner(path_to_sceanrios: list[str], ctx_manager: IContextManager) -> ScenarioRunnner:
    runnner = ScenarioRunnner(scenarios={}, context_manager=ctx_manager)
    ctx_manager
    for p in path_to_sceanrios:
        files = glob.glob(p)
        for file in files:
            scenario = parse_scenario(file)
            if scenario:
                runnner.add_scenario(scenario)
    return runnner