import os
from typing import Any, Literal
from pydantic import BaseModel
from aiogram.types import Message
from aiogram import Bot
from abc import ABC, abstractmethod
from yako.exceptions import NoNextNode, NotExistsNode

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))

class Context:
    def __init__(self) -> None:
        self._context_vars: dict[str, Any] = {}
        self.current_node: str = 'start_node'
        self.current_scenario: str = ''


class Action(BaseModel, ABC):
    @abstractmethod
    async def run(self, ctx: Context, current_message: Message):
        pass

class PyAction(Action):
    type: Literal['python']
    code: str
    
    async def run(self, ctx: Context, current_message: Message):
        exec(self.code, {"state": ctx._context_vars, "message": current_message})

class ModuleAction(Action):
    type: Literal['module']
    name: str
    
    async def run(self, ctx: Context, current_message: Message):
        pass

class NodeAction(Action):
    type: Literal['node']
    name: str

    async def run(self, ctx: Context, current_message: Message):
        pass


class Node(BaseModel):
    name: str
    text: str | None = None
    next_nodes: list[str] = []
    action: NodeAction | ModuleAction | PyAction | None = None
    compile_formatting: bool | None = None
    next_node_instantly: bool = False
    
    async def run(self, ctx: Context, current_message: Message):
        if self.text:
            if self.compile_formatting:
                self.text = eval(self.text, {"state": ctx._context_vars, "message": current_message})
            await bot.send_message(current_message.chat.id, self.text)
        if self.action:
            await self.action.run(ctx, current_message)
        if not self.next_nodes:
            raise NoNextNode
        ctx.current_node = self.next_nodes[0] # TODO поправить
    

class Scenario(BaseModel):
    name: str
    run_condition: str
    nodes: dict[str, Node]
    
    async def run(self, ctx: Context, current_message: Message):
        node = self.nodes[ctx.current_node]
        if not node:
            raise NotExistsNode
        await node.run(ctx, current_message)

        if node.next_node_instantly:
            await self.run(ctx, current_message)
        
    def is_suitable(self, current_message: Message) -> bool:
        try:
            result = eval(self.run_condition, {"message": current_message})
        except Exception:
            return False
        if isinstance(result, bool):
            return result
        return False