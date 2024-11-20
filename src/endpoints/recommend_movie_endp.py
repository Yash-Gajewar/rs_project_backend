from fastapi import APIRouter
# from src.operations.recommend_movie import recommend_movie, fetch_movie_id, fetch_movie_details

from src.operations.recommend_movie import recommend_top_5, content_based_recommendation

from typing import List


router = APIRouter(
    prefix="/api/recommend_movie",
    tags=["recommend_movie"],
    responses={404: {"description": "Not found"}},
)


@router.post("/top_5")
async def get_top_5(genre_list: List[str]):
    return recommend_top_5(genre_list)


@router.get("/content_based")
async def get_content_based(movie_name: str):
    return content_based_recommendation(movie_name)





   



    
