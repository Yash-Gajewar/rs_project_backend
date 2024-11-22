from fastapi import APIRouter
# from src.operations.recommend_movie import recommend_movie, fetch_movie_id, fetch_movie_details

from src.operations.recommend_movie import recommend_top_5, content_based_recommendation, collaborative_filter

from typing import List, Dict

from src.models.user_model import UserRatingsRequest


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



@router.post("/collaborative_based")
async def recommend_movies(user_ratings_request: UserRatingsRequest):
    # Extract the list of movies and ratings
    user_ratings = [
        {"movie": rating.movie, "rating": rating.rating}
        for rating in user_ratings_request.ratings
    ]

    # Call your collaborative_filter function with the correct format
    recommendations = collaborative_filter(user_ratings)
    return {"recommendations": recommendations}






   



    
