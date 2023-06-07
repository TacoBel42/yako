from importlib.machinery import SourceFileLoader
import os
import importlib
from typing import Any, Literal

from pydantic import BaseModel
from aiogram.types import Message
from aiogram import Bot
from abc import ABC, abstractmethod
from yako.exceptions import NoModule, NoNextNode, NotExistsNode

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
        
class Context:
    def __init__(self) -> None:
        self._context_vars: dict[str, Any] = {}
        self.current_node: str = 'start_node'
        self.current_scenario: str = ''
        self.current_message: Message | None = None
        self.modules: dict[str, RunnableModule] = {}

class RunnableModule:
    
    def __init__(self, name: str, path: str):
        self.path = path
        self.name = name
        self._module = SourceFileLoader(self.name, path).load_module()
        self._module.init()
    
    async def execute(self, vars: dict[str, Any], message: Message) -> dict[str, Any]:
        return await self._module.call(vars, message)

class Action(BaseModel, ABC):
    @abstractmethod
    async def run(self, ctx: Context):
        pass

class PyAction(Action):
    type: Literal['python']
    code: str
    
    async def run(self, ctx: Context):
        exec(self.code, {"state": ctx._context_vars, "message": ctx.current_message})

class ModuleAction(Action):
    type: Literal['module']
    name: str
    
    async def run(self, ctx: Context):
        module = ctx.modules.get(self.name)
        if not module:
            raise NoModule
        vars = await module.execute(ctx._context_vars, ctx.current_message)
        ctx._context_vars = vars

class NodeAction(Action):
    type: Literal['node']
    name: str

    async def run(self, ctx: Context):
        # todo send ctx.vars, bot, message
        pass

class Node(BaseModel):
    class CondidtionNode(BaseModel):
        type: Literal['condition']
        name: str
        condition: str
    
    name: str
    text: str | None = None
    next_nodes: list[str] | list[CondidtionNode] = []
    action: NodeAction | ModuleAction | PyAction | None = None
    compile_formatting: bool | None = None
    next_node_instantly: bool = False
    
    async def run(self, ctx: Context):
        text = self.text
        if self.text:
            if self.compile_formatting:
                text = eval(self.text, {
                    "state": ctx._context_vars, "message": ctx.current_message
                    })
            await bot.send_message(ctx.current_message.chat.id, text)
        if self.action:
            await self.action.run(ctx)
        if not self.next_nodes:
            raise NoNextNode
        if len(self.next_nodes) == 1 and isinstance(self.next_nodes[0], str):
            ctx.current_node = self.next_nodes[0]
        else:
            ctx.current_node = self._get_next_node(ctx)
    
    def _get_next_node(self, ctx: Context):
        for node in self.next_nodes:
            if eval(node.condition, {"state": ctx._context_vars, "message": ctx.current_message}):
                return node.name
        raise NoNextNode
    

class Scenario(BaseModel):
    name: str
    run_condition: str
    nodes: dict[str, Node]
    
    class Config:
        arbitrary_types_allowed = True
    
    scenario_modules: dict[str, RunnableModule]
    
    async def run(self, ctx: Context):
        node = self.nodes[ctx.current_node]
        if not node:
            raise NotExistsNode
        await node.run(ctx)

        if node.next_node_instantly: # TODO: recursion deep
            await self.run(ctx)
        
    def is_suitable(self, message: Message) -> bool:
        try:
            result = eval(self.run_condition, {"message": message})
        except Exception:
            return False
        if isinstance(result, bool):
            return result
        return False