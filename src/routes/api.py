from fastapi import APIRouter
from src.endpoints import recommend_movie_endp, user_endp



router = APIRouter()
router.include_router(recommend_movie_endp.router)
router.include_router(user_endp.router)





