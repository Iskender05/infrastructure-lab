from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
    ]
    description: str = ""
    completed: bool = False


class TaskResponse(TaskInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
