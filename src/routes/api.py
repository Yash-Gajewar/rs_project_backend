from fastapi import APIRouter
from src.endpoints.recommend_movie_endp import router as recommend_movie_router

router = APIRouter()
router.include_router(recommend_movie_router)





