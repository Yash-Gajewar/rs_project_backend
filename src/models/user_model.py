from pydantic import BaseModel
from typing import List
from pydantic import Field
from typing import Dict



class User(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)
    genre : List[str] = Field(...)



class MovieRatings(BaseModel):
    rating: Dict[str, int] = Field(..., description="A dictionary mapping movie titles to ratings.")



class UserRating(BaseModel):
    movie: str = Field(..., description="The title of the movie.")
    rating: float = Field(..., description="The rating given to the movie.")

class UserRatingsRequest(BaseModel):
    ratings: List[UserRating] = Field(..., description="List of movies with ratings.")