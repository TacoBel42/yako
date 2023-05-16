from pydantic import BaseModel
from aiogram.types import Message
from yako.parser import parse_scenario

from yako.scenario import Context, Scenario

class ScenarioRunnner(BaseModel):
    scenarios: dict[str, Scenario]
    
    async def run(self, ctx: Context, current_message: Message):
        suitable_scenario = None
    
        if ctx.current_scenario:
            suitable_scenario = self.scenarios[ctx.current_scenario]
        if not ctx.current_scenario:
            for scenario_name, scenario in self.scenarios.items():
                if scenario.is_suitable(current_message):
                    ctx.current_scenario = scenario_name
                    suitable_scenario = scenario
        if not suitable_scenario:
            return 
        await suitable_scenario.run(ctx, current_message)
    
    def add_scenario(self, scenario: Scenario):
        self.scenarios[scenario.name] = scenario
        
def init_runner(path_to_sceanrios: list[str]):
    runnner = ScenarioRunnner(scenarios={})
    for p in path_to_sceanrios:
        scenario = parse_scenario(p)
        runnner.add_scenario(scenario)
    return runnner