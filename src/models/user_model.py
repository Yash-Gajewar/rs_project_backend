from pydantic import BaseModel
from typing import List
from pydantic import Field


class User(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)
    genre : List[str] = Field(...)
