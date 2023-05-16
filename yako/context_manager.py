from pydantic import BaseModel

from yako.scenario import Context

class ContextManager(BaseModel):
    _ctxs: dict[str, Context] = {}
    
    def get_context(self, identity_key: str):
        if not self._ctxs.get(identity_key):
            self._ctxs[identity_key] = Context()
        return self._ctxs[identity_key]
