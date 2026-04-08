from pydantic import BaseModel

class EmailObservation(BaseModel):
    email_text: str
    task_type: str


class EmailAction(BaseModel):
    response: str


class StepResult(BaseModel):
    observation: EmailObservation
    reward: float
    done: bool
    info: dict = {}