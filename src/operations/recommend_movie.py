import pandas as pd
import re
import requests
import ast
from typing import List


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
    

def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=83b44cdf02bdd95a7c2fa4ab67514e6a&language=en-US"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": f"Failed to fetch details for movie ID {movie_id}"}
        response_json = response.json()
        return {
            'poster_path': f"https://image.tmdb.org/t/p/w500/{response_json.get('poster_path', '')}",
            'movie': response_json.get('original_title', 'No title available'),
            'overview': response_json.get('overview', 'No overview available'),
            'tagline': response_json.get('tagline', '')
        }
    except Exception as e:
        return {"error": str(e)}



# Main function to recommend top 5 movies for each genre
    
def recommend_top_5(genre_list: List[str]):
    df = pd.read_csv('./tmdb_5000_movies.csv')
    df['genres'] = df['genres'].apply(convert)  # Ensure genres are lists
    movies = df[['id', 'title', 'overview', 'genres', 'keywords', 'vote_average']]
    
    top_movies = []

    for genre in genre_list:
        genre_movies = movies[movies['genres'].apply(lambda x: genre in x)]
        if genre_movies.empty:
            continue  # Skip genres with no movies
    
    genre_movies = genre_movies.sort_values(by='vote_average', ascending=False)
    genre_movies = genre_movies.head(5)

    for _, row in genre_movies.iterrows():
        details = fetch_movie_details(row['id'])
        if 'error' not in details:
            top_movies.append(details)

    return top_movies




    

    
