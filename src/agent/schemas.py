from pydantic import BaseModel


class AgentRequest(BaseModel):
    message: str
    conversation_id: str = ""
    max_iterations: int = 5


class AgentStepResponse(BaseModel):
    step_type: str  # thought / action / observation / answer
    content: str
    tool_name: str = ""
    tool_args: dict = {}


class AgentResponse(BaseModel):
    answer: str
    steps: list[AgentStepResponse]
    conversation_id: str
