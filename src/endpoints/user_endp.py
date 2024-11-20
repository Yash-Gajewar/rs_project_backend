from fastapi import HTTPException, APIRouter
from src.models.user_model import User
# from pymongo import ASCENDING


from src.establish_db_connection import database


collection = database.Users

# collection.create_index([("email", ASCENDING)], unique=True)


router = APIRouter(
    prefix="/api/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post("/createuser")
async def post_user(user: User):
    try:
        document = user.dict()  # Convert Pydantic model to dict
        result = collection.insert_one(document)  # Insert into MongoDB
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}
    

@router.get("/userexists")
async def get_user(email :str, password:str):
    result = collection.find_one({"email": email, "password": password})
    if result is not None:
        return True
    else:
        return False



       
