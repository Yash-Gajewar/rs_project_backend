from fastapi import APIRouter
# from src.operations.recommend_movie import recommend_movie, fetch_movie_id, fetch_movie_details

from src.operations.recommend_movie import recommend_top_5, content_based_recommendation, collaborative_filter, fetch_movie_details

from typing import List, Dict


router = APIRouter(
    prefix="/api/recommend_movie",
    tags=["recommend_movie"],
    responses={404: {"description": "Not found"}},
)


@router.post("/top_5")
async def get_top_5(genre: str):
    return recommend_top_5(genre)


@router.get("/content_based")
async def get_content_based(movie_name: str):
    return content_based_recommendation(movie_name)



@router.get("/collaborative_based")
async def get_collaborative_filter(username : str):
    # Call your collaborative_filter function with the correct format
    recommendations = await collaborative_filter(username)
    # return {"recommendations": recommendations}

    return recommendations



@router.get("/get_movie_details")
async def get_movie_details(movie_name: str):
    return fetch_movie_details(movie_name)








   



    
