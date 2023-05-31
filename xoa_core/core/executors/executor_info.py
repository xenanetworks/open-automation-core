from pydantic import BaseModel


class ExecutorInfo(BaseModel):
    id: str
    suite_name: str
    state: str
