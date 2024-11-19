import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import re
import requests


import re
import pandas as pd

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
    movies = pd.read_csv('https://portfolio-project-images-yash.s3.ap-south-1.amazonaws.com/tmdb_5000_movies.csv', 
                         usecols=['id', 'original_title'], 
                         dtype={'id': 'int32', 'original_title': 'str'})

    # Find the movie by matching the corrected movie name
    movie_row = movies[movies['original_title'] == movie_name_cleaned]
    
    if not movie_row.empty:
        return movie_row['id'].iloc[0]
    else:
        return None

    

# curl --request GET \
#      --url 'https://api.themoviedb.org/3/movie/209112?language=en-US' \
#      --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4M2I0NGNkZjAyYmRkOTVhN2MyZmE0YWI2NzUxNGU2YSIsIm5iZiI6MTcyODkyNjEwNC42MTQ4NjksInN1YiI6IjY3MGQ1MGM1ZjU4YTkyMDZhYTQxODI4YyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.K_4bSJOop772JQ66j4taMlnQD0DtIZi-Ny3imLdx33s' \
#      --header 'accept: application/json'
    

def fetch_movie_details(movie_id):
    result = {}
    url = "https://api.themoviedb.org/3/movie/{0}?api_key=83b44cdf02bdd95a7c2fa4ab67514e6a&language=en-US".format(movie_id)
    response = requests.get(url)
    response_json = response.json()

    # Check if 'poster_path' exists in the response
    poster_path = response_json.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        full_path = None  # Or provide a default image URL if necessary

    result['poster_path'] = full_path
    result['movie'] = response_json.get('original_title', 'No title available')
    result['overview'] = response_json.get('overview', 'No overview available')
    result['tagline'] = response_json.get('tagline', '')

    return result



def recommend_movie(movie_name):
    # Load the data
    movies_df = pd.read_csv('https://portfolio-project-images-yash.s3.ap-south-1.amazonaws.com/movies.csv', usecols=['movieId', 'title'], dtype={'movieId': 'int32', 'title': 'str'})
    rating_df = pd.read_csv('https://portfolio-project-images-yash.s3.ap-south-1.amazonaws.com/ratings.csv', usecols=['userId', 'movieId', 'rating'], dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
    
    # Merge data
    df = pd.merge(rating_df, movies_df, on='movieId')
    combine_movie_rating = df.dropna(axis=0, subset=['title'])
    
    # Count movie ratings
    movie_ratingCount = (combine_movie_rating
                         .groupby(by=['title'])['rating']
                         .count()
                         .reset_index()
                         .rename(columns={'rating': 'totalRatingCount'})
                         [['title', 'totalRatingCount']])
    
    # Merge with rating count
    rating_with_totalRatingCount = combine_movie_rating.merge(movie_ratingCount, left_on='title', right_on='title', how='left')
    
    # Filter popular movies
    popularity_threshold = 50
    rating_popular_movie = rating_with_totalRatingCount.query('totalRatingCount >= @popularity_threshold')
    
    # Pivot data to create movie features
    movie_features_df = rating_popular_movie.pivot_table(index='title', columns='userId', values='rating').fillna(0)
    movie_features_df_matrix = csr_matrix(movie_features_df.values)
    
    # Train the model
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(movie_features_df_matrix)
    
    # Check if the movie exists in the dataset
    if movie_name not in movie_features_df.index:
        return {'error': 'Movie not found'}
    
    # Get recommendations
    query_index = movie_features_df.index.get_loc(movie_name)
    distances, indices = model_knn.kneighbors(movie_features_df.iloc[query_index, :].values.reshape(1, -1), n_neighbors=6)
    
    recommendations = []
    for i in range(1, len(distances.flatten())):
        recommendations.append(movie_features_df.index[indices.flatten()[i]])

    
    result = {}


    for movie in recommendations:
        movie_id = fetch_movie_id(movie)
        movie_details = fetch_movie_details(movie_id)
        result[movie] = movie_details
        result[movie]['title'] = fix_movie_title(movie)

    return result

    


    

    
