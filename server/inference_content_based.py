import pandas as pd
import json
import statistics
from fuzzywuzzy import process
from .base import Base


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


class ContentBasedFilter(Base):
    def __init__(self):
        super().__init__()
        self.user_movie_matrix = self.load('user_movie_matrix_cbf.npz', as_df=True)
        self.user_movie_matrix_cols = self.load('user_movie_matrix_cbf_cols.npz')
        self.user_movie_matrix = self.user_movie_matrix.set_index(0)
        self.user_movie_matrix.columns = self.user_movie_matrix_cols.tolist()

        self.ratings_df_cbf = self.load('ratings_df_cbf.npz', as_df=True, columns=['title', 'average_rating', 'num_of_ratings'])
        self.ratings_df_cbf = self.ratings_df_cbf.set_index('title')

    def recommend_content_based(self, movie_name, min_num_reviews=50, n_recommendations=10):
        movie_name = process.extractOne(movie_name, self.movies_df['title'])[0]
        # Get user ratings for film
        movie_x_user_ratings = self.user_movie_matrix[movie_name]
        # Create pandas series of correlations for all movie with movie_x
        similar_to_movie_x = self.user_movie_matrix.corrwith(movie_x_user_ratings)
        # Convert to df

        corr_movie_x = pd.DataFrame(similar_to_movie_x, columns=['Correlation'])
        # Drop nulls
        corr_movie_x.dropna(inplace=True)
        # Join ratings info to enbale filtering of films with low nums of ratings
        corr_movie_x = corr_movie_x.join(self.ratings_df_cbf['num_of_ratings'])
        # Apply filter
        new_corr_movie_x = corr_movie_x[corr_movie_x['num_of_ratings'] >= min_num_reviews]

        movies = []
        for index, row in new_corr_movie_x.iterrows():
            movie = self.movies_df[self.movies_df['title'] == index].iloc[0]
            full_movie = self.movies_df_full[self.movies_df_full['title'] == index].iloc[0]
            ratings = self.ratings_df[self.ratings_df['movieId'] == movie.movieId]['rating']
            movies.append({
                'id': int(movie.movieId),
                'title': movie.title,
                'correlation': float(row.Correlation),
                'no_of_ratings': int(row.num_of_ratings),
                'rating': float(statistics.mean(ratings if len(ratings) > 0 else [0])),
                'genres': [genre['name'] for genre in json.loads(movie.genres.replace("'", '"'))],
                'more_info': {
                    **full_movie.drop(['genres', 'id', 'title'])
                }
            })
        # Sort intp ascending order
        movies_movies = sorted(
            movies,
            key=lambda d: (d['correlation'], d['no_of_ratings'], -d['rating']),
            reverse=True,
        )
        return movies_movies[1:n_recommendations+1]


if __name__ == '__main__':
    from pprint import pprint
    from tqdm import tqdm
    import numpy as np
    import traceback
    user_id = 50
    recommender = ContentBasedFilter()
    h = recommender.user_movie_matrix
    breakpoint()
    # print(list(recommender.movies_df['title']))
    # movies = recommender.recommend_content_based('Jurassic Park', n_recommendations=1, min_num_reviews=70)
    # movies = recommender.recommend_content_based('Jurassic Park', n_recommendations=10, min_num_reviews=70)
    movies = list(set(list(recommender.movies_df['title'])))
    valid_movies = []
    for i, movie in enumerate(tqdm(movies)):
        if i % 1000 == 0:
            print("saving ", i)
            print(len(valid_movies))
            np.savez_compressed("valid_movies_cb.npz", valid_movies)
        try:
            recommender.recommend_content_based(movie, n_recommendations=10)
            valid_movies.append(movie)
        except Exception as e:
            traceback.print_exc()
            pass
    np.savez_compressed("valid_movies_cb.npz", valid_movies)
    print(f"{len(movies) - len(valid_movies)} failed")
    # 42277
    # breakpoint()
    pprint(movies)

