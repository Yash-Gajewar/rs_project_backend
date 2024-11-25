from fastapi import HTTPException, APIRouter
from src.models.user_model import User, Genre
# from pymongo import ASCENDING


from src.establish_db_connection import database

from typing import List


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
    

@router.post("/genre")
async def add_genre(email: str, genre: Genre):
    # Find the user by email
    result = collection.find_one({"email": email})

    if result:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string for JSON compatibility

        # Initialize or update the genre field
        if "genre" not in result:
            result["genre"] = []

        result["genre"] = genre.genre

        # Save the updated user data back to the database
        collection.update_one({"email": email}, {"$set": {"genre": result["genre"]}})

        return {"message": "Genres added successfully", "user": result}

    # If user is not found
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/post_ratings")
async def post_ratings(email: str, ratings: List[str]):
    # Ensure the ratings list has exactly two elements
    if len(ratings) != 2:
        return {"error": "Invalid ratings format. Provide [movie, rating]."}

    movie_name, rating = ratings[0], ratings[1]

    # Find the user by email
    result = collection.find_one({"email": email})

    if result:
        result["_id"] = str(result["_id"])

        # Initialize or update the ratings field
        if "ratings" not in result:
            result["ratings"] = {}

        # Update the ratings dictionary
        result["ratings"][movie_name] = rating

        # Save the updated user data back to the database
        collection.update_one({"email": email}, {"$set": {"ratings": result["ratings"]}})

        return {"message": "Ratings added successfully", "user": result}
    else:
        return {"error": "User not found"}

        



@router.get("/get_ratings")
async def get_ratings(email: str):
    result = collection.find_one({"email": email})
    if result is not None:
        return result["ratings"]
    else:
        return {"error": "User not found"}
    




