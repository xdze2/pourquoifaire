from sqlmodel import SQLModel, Field


class Node(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str
    context: str = ""
    status: str = "pending"
    type: str = "task"
