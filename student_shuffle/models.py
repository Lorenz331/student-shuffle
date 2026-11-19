from pydantic import BaseModel, Field
from datetime import date

class Session(BaseModel):
    date: date
    graded: tuple[str, ...]
    practice: list[tuple[str, ...]]

class History(BaseModel):
    students: list[str] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)
