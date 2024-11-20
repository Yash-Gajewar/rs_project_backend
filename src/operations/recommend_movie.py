import pandas as pd
import re
import requests
import ast
from typing import List
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity



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

def recommend_top_5(genre_list: List[str]):
    
    # Load the dataset
    df = pd.read_csv('./tmdb_5000_movies.csv')

    # Convert genres column into a list of genre names
    df['genres'] = df['genres'].apply(convert)  

    # Select relevant columns
    movies = df[['id', 'title', 'overview', 'genres', 'keywords', 'vote_average']]

    # Dictionary to store top 5 movies for each genre
    top_movies = {}

    # Get top 5 movies for each genre
    for genre in genre_list:
        genre_movies = movies[movies['genres'].apply(lambda x: genre in x)]  # Filter by genre
        genre_movies = genre_movies.sort_values(by='vote_average', ascending=False)  # Sort by ratings
        top_movies[genre] = genre_movies.head(5).to_dict(orient='records')  # Convert to JSON-like dict

    # Optionally, pretty print the results for debugging
    print(json.dumps(top_movies, indent=4))

    # Return the top_movies dictionary for use in API responses
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




def fetch_movie_details(movie_id):
    try:
        df = pd.read_csv('./tmdb_5000_movies.csv')
        df.dropna(subset=['genres', 'keywords', 'cast', 'crew'], inplace=True)
        movie = df[df['id'] == movie_id]
        if movie.empty:
            return {"error": f"Failed to fetch details for movie ID {movie_id}"}
        movie = movie.iloc[0]
        return {
            'title': movie.get('original_title', 'No title available'),
            'overview': movie.get('overview', 'No overview available') or 'No overview available',
            'tagline': movie.get('tagline', '') or ''
        }

    except Exception as e:
        return {"error": str(e)}


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

    return recommended_movies












    

    
