from sqlmodel import SQLModel, Field


class Node(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str
    context: str = ""
    status: str = "pending"
    type: str = "task"


class Link(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    src: int = Field(foreign_key="node.id")
    tgt: int = Field(foreign_key="node.id")
    link_type: str = Field(default="why")
