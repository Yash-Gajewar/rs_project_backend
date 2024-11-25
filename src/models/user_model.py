from pydantic import BaseModel
from typing import List
from pydantic import Field
from typing import Dict



class User(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)


class Genre(BaseModel):
    genre: List[str] = Field(..., description="List of genres.")





