from fastapi import APIRouter
from src.operations.recommend_movie import recommend_movie, fetch_movie_id, fetch_movie_details


router = APIRouter(
    prefix="/api/recommend_movie",
    tags=["recommend_movie"],
    responses={404: {"description": "Not found"}},
)



@router.get("/")
async def get_recommend_movie(movie_name: str):
    return recommend_movie(movie_name)



@router.get("/movie_details")
async def get_movie_details(movie_id: int):
    return fetch_movie_details(movie_id)





   



    
