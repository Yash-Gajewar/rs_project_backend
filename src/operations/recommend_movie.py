import pandas as pd
import re
import ast
from typing import List, Dict
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.endpoints.user_endp import get_ratings


from src.establish_db_connection import database

collection = database.Users


def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L


def fix_movie_title(movie_name):
    """
    This function detects movie titles in the format 'Title, The (Year)' or 'Title, A (Year)'
    and converts them into 'The Title' or 'A Title', respectively.
    """
    # Remove the release year in parentheses (e.g., (2001))
    movie_name_cleaned = re.sub(r'\s*\(\d{4}\)', '', movie_name)

    # Use a regex to find if there is a comma followed by 'The', 'A', or 'An' and reorder them
    fixed_title = re.sub(r'^(.*),\s*(The|A|An)$', r'\2 \1', movie_name_cleaned)
    
    return fixed_title


def fetch_movie_id(movie_name):
    # Fix the movie title to reorder if needed
    movie_name_cleaned = fix_movie_title(movie_name)

    # Load the movie dataset
    movies = pd.read_csv('./tmdb_5000_movies.csv', 
                         usecols=['id', 'original_title'], 
                         dtype={'id': 'int32', 'original_title': 'str'})

    # Find the movie by matching the corrected movie name
    movie_row = movies[movies['original_title'] == movie_name_cleaned]
    
    if not movie_row.empty:
        return movie_row['id'].iloc[0]
    else:
        return None
    

# def fetch_movie_details(movie_id):
#     try:
#         url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=83b44cdf02bdd95a7c2fa4ab67514e6a&language=en-US"
#         response = requests.get(url)
#         if response.status_code != 200:
#             return {"error": f"Failed to fetch details for movie ID {movie_id}"}
#         response_json = response.json()
#         return {
#             'poster_path': f"https://image.tmdb.org/t/p/w500/{response_json.get('poster_path', '')}",
#             'movie': response_json.get('original_title', 'No title available'),
#             'overview': response_json.get('overview', 'No overview available'),
#             'tagline': response_json.get('tagline', '')
#         }
#     except Exception as e:
#         return {"error": str(e)}



# Main function to recommend top 5 movies for each genre

from typing import List
import pandas as pd

def recommend_top_5(genre: str):
    # Load the dataset
    df = pd.read_csv('./tmdb_5000_movies.csv')

    # Convert genres column into a list of genre names
    df['genres'] = df['genres'].apply(convert)  

    # Select relevant columns
    movies = df[['id', 'title', 'overview', 'genres', 'keywords', 'vote_average']]

    genre_list = genre.split(',')  # Convert to list

    # List to store top movies
    top_movies = []

    # Get top 5 movies for each genre
    for genre in genre_list:
        genre_movies = movies[movies['genres'].apply(lambda x: genre in x)]  # Filter by genre
        genre_movies = genre_movies.sort_values(by='vote_average', ascending=False)  # Sort by ratings
        top_movies.extend(genre_movies.head(5).to_dict(orient='records'))  # Add to the list

    # Return a flat list of top movies

    return top_movies


def convert3(text):
    L = []
    counter = 0
    for i in ast.literal_eval(text):
        if counter < 3:
            L.append(i['name'])
        counter+=1
    return L


def fetch_director(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L


def collapse(L):
    L1 = []
    for i in L:
        L1.append(i.replace(" ",""))
    return L1



# fetch movie details like id, original_title, overview, tagline, poster_path from ./tmdb5000_movies.csv from movie title

def fetch_movie_details(movie_title):
    """
    Fetches movie details from the CSV file based on the movie title.

    Args:
        file_path (str): Path to the tmdb5000_movies.csv file.
        movie_title (str): Title of the movie to search for.

    Returns:
        dict: A dictionary containing movie details or a message if the movie is not found.
    """
    try:
        # Load the CSV file
        movies_df = pd.read_csv('./tmdb_5000_movies.csv')
        
        # Perform a case-insensitive search for the movie title
        movie = movies_df[movies_df['title'].str.lower() == movie_title.lower()]
        
        if movie.empty:
            return {"error": "Movie not found."}
        
        # Extract relevant details
        movie = movie.iloc[0]  # First match
        details = {
            "id": int(movie['id']),  # Ensure proper type conversion
            "name": str(movie['original_title']),
            "overview": str(movie['overview']),
            "tagline": str(movie['tagline']) if pd.notna(movie['tagline']) else None,
            "poster_path": None  # Not present in the dataset
        }
        return details
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


    


def content_based_recommendation(movie_name : str):
    movies = pd.read_csv('./tmdb_5000_movies.csv')
    credits = pd.read_csv('./tmdb_5000_credits.csv')


    movies = movies.merge(credits,on='title')
    movies = movies[['title','genres','keywords','cast','crew']]

    movies.dropna(inplace=True)

    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)

    ast.literal_eval('[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 14, "name": "Fantasy"}, {"id": 878, "name": "Science Fiction"}]')
    movies['cast'] = movies['cast'].apply(convert)


    movies['cast'] = movies['cast'].apply(lambda x:x[0:3])
    movies['crew'] = movies['crew'].apply(fetch_director)

    movies['cast'] = movies['cast'].apply(collapse)
    movies['crew'] = movies['crew'].apply(collapse)
    movies['genres'] = movies['genres'].apply(collapse)
    movies['keywords'] = movies['keywords'].apply(collapse)


    movies['tags'] = movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']


    new = movies.drop(columns=['genres','keywords','cast','crew'])

    new['tags'] = new['tags'].apply(lambda x: " ".join(x))

    cv = CountVectorizer(max_features=5000,stop_words='english')

    vector = cv.fit_transform(new['tags']).toarray()

    similarity = cosine_similarity(vector)

    new[new['title'] == 'The Lego Movie'].index[0]

    recommended_movies = []

    index = new[new['title'] == movie_name].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    for i in distances[1:11]:
        recommended_movies.append(new.iloc[i[0]].title)

    result = []

    for i in recommended_movies:
        result.append(fetch_movie_details(i))

    return result



def get_similar(movie: str, rating: float, corrMatrix: pd.DataFrame) -> pd.Series:
    """
    Calculate similarity scores for a given movie.
    """
    if movie in corrMatrix:
        similar_scores = corrMatrix[movie] * (rating - 2.5)  # Weight by how much user liked the movie
        return similar_scores
    return pd.Series()  # Return empty series if the movie is not in the correlation matrix




async def collaborative_filter(username: str):
    result = collection.find_one({"username": username})
    if result is not None:
        # return result["ratings"]

        user = []

        for key, value in  result["ratings"].items():
            user.append({"movie": key, "rating": float(value)})

        ratings = pd.read_csv('./ratings.csv')
        movies = pd.read_csv('./movies.csv')
        
        # Merge and preprocess data
        ratings = pd.merge(movies, ratings).drop(['genres', 'timestamp'], axis=1)
        userRatings = ratings.pivot_table(index=['userId'], columns=['title'], values='rating')
        userRatings = userRatings.dropna(thresh=10, axis=1).fillna(0, axis=1)
        corrMatrix = userRatings.corr(method='pearson')

        # Generate recommendations
        similar_movies = pd.DataFrame()
        for entry in user:
            movie = entry['movie']
            rating = entry['rating']
            similar = get_similar(movie, rating, corrMatrix).to_frame().T
            similar_movies = pd.concat([similar_movies, similar], ignore_index=True)

        # Aggregate and sort recommendations
        recommended = similar_movies.sum().sort_values(ascending=False).head(10)

        recommended_list = recommended.index.tolist()  # Return the top 10 movie titles

        result = []

        for movie in recommended_list:
            temp_title = fix_movie_title(movie)
            details = fetch_movie_details(temp_title)
            result.append(details)


        return result
            
    else:
        return {"error": "User not found"}












    

    
