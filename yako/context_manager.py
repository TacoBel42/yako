from abc import ABC, abstractmethod
from pydantic import BaseModel

from yako.scenario import Context

class IContextManager(BaseModel, ABC):
    _ctxs: dict[str, Context] = {}

    @abstractmethod
    def get_context(self, identity_key: str) -> Context: 
        pass
    
    @abstractmethod
    def drop_context(self, identity_key: str):
        pass
    
    
class ContextManager(IContextManager):
    
    def get_context(self, identity_key: str) -> Context:
        if not self._ctxs.get(identity_key):
            self._ctxs[identity_key] = Context()
        return self._ctxs[identity_key]
    
    def drop_context(self, identity_key: str):
        if identity_key not in self._ctxs:
            return
        self._ctxs.pop(identity_key)
