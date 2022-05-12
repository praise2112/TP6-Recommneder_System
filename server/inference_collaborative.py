import numpy as np
import pandas as pd
import traceback
import json
from fuzzywuzzy import process
from scipy.sparse import csr_matrix
import statistics
try:
    from .base import Base, clean
except:
    from  base import Base, clean


class CollaborativeFilter(Base):
    def __init__(self):
        super().__init__()
        self.merged_df = self.load('merged_df.npz', as_df=True, columns=['userId', 'movieId', 'rating', 'timestamp', 'title', 'genres'])
        self.ratings_matrix_items = self.load('ratings_matrix_items_cf.npz', as_df=True)
        self.model_KNN = self.load('model_knn_cf.pkl', from_pkl=True)
        self.mat_movies_users = csr_matrix(self.ratings_matrix_items.values)

    def item_similarity(self, movie_name):
        try:
            user_inp = movie_name
            inp = self.movies_df[self.movies_df['title'].str.contains(user_inp)].index.tolist()
            inp = inp[0]
            self.movies_df['similarity'] = self.ratings_matrix_items.iloc[inp]
            self.movies_df.columns = ['movieId', 'title', 'genres', 'similarity']
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def _recommend_movies_item_similarity(self, user_id=None, movie_name=None, n_recommendations=10):
        """
         Recommending movie which user hasn't watched as per Item Similarity
        :param movie_name:
        :param n_recommendations:
        :param user_id: user_id to whom movie needs to be recommended
        :return: movieIds to user
        """
        user_movie = movie_name
        if not user_movie:
            user_movie = self.merged_df[(self.merged_df.userId == user_id)].sort_values(["rating"], ascending=False)[['title']]
            user_movie = user_movie.title.iloc[0]
        is_movie_valid = self.item_similarity(user_movie)
        if not is_movie_valid:
            return {}

        sorted_movies_as_per_userChoice = self.movies_df.sort_values(["similarity"], ascending=False)
        sorted_movies_as_per_userChoice = \
        sorted_movies_as_per_userChoice[sorted_movies_as_per_userChoice['similarity'] >= 0.15]['movieId']

        df_recommended_item = pd.DataFrame()
        user2Movies = self.ratings_df[self.ratings_df['userId'] == user_id]['movieId']
        for movieId in sorted_movies_as_per_userChoice:
            if movieId not in user2Movies:
                df_new = self.ratings_df[(self.ratings_df.movieId == movieId)]
                df_recommended_item = pd.concat([df_recommended_item, df_new])

        df_recommended_item = df_recommended_item.sort_values(["rating"], ascending=False).drop_duplicates(
            subset=['movieId'], keep='first')
        return df_recommended_item[['movieId', 'rating']][:n_recommendations].to_dict()

    def recommend_movies_item_similarity(self, *args, **kwargs):
        old_n_r = kwargs['n_recommendations']
        n_r = max(100, kwargs['n_recommendations'])
        del kwargs['n_recommendations']
        ids = self._recommend_movies_item_similarity(*args, n_recommendations=n_r, **kwargs)
        return self.movieIds_to_title(ids, n_recommendations=old_n_r)

    def movieIds_to_title(self, movie_dict, n_recommendations):
        """
         Converting movieId to titles
        :param movie_dict: dict of movies
        :return: movie titles
        """
        movie_titles = []
        for id in movie_dict['movieId'].keys():
            row = self.movies_df[self.movies_df['movieId'] == movie_dict['movieId'][id]].iloc[0]
            full_movie = self.movies_df_full[self.movies_df_full['title'] == row.title].iloc[0]
            movie_titles.append({
                'id': int(id),
                'title': row.title,
                'rating': float(movie_dict['rating'][id]),
                'similarity': round(row.similarity, 2),
                'no_of_ratings':  int((self.ratings_df['movieId'] == movie_dict['movieId'][id]).sum()),
                'genres': [genre['name'] for genre in json.loads(row.genres.replace("'", '"'))],
                'more_info': clean({
                    **full_movie.drop(['genres', 'id', 'title'])
                })
            })
        sorted_movies = sorted(movie_titles, key=lambda d: (d['similarity'], d['no_of_ratings'], -d['rating']), reverse=True)
        return sorted_movies[:n_recommendations]

    def recommend_KNN(self, n_recommendations=10, movie_name=None, user_id=None):
        if user_id:
            movie_name = self.merged_df[(self.merged_df.userId == user_id)].sort_values(["rating"], ascending=False)[['title']]
            movie_name = movie_name.title.iloc[0]
        movie_index = process.extractOne(movie_name, self.movies_df['title'])[2]

        distances, indices = self.model_KNN.kneighbors(self.mat_movies_users[movie_index], n_neighbors=n_recommendations)
        recc_movie_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                                    key=lambda x: x[1])[:0:-1]
        movies = []
        for val in recc_movie_indices:
            row = self.movies_df.iloc[val[0]]
            full_movie = self.movies_df_full[self.movies_df_full['title'] == row.title].iloc[0]
            ratings = self.ratings_df[self.ratings_df['movieId'] == row.movieId]['rating']
            movies.append({
                'title': row.title,
                'id': int(row.movieId),
                'rating': float(statistics.mean(ratings if len(ratings) > 0 else [0])),
                'no_of_ratings': int((self.ratings_df['movieId'] == row.movieId).sum()),
                'genres': [genre['name'] for genre in json.loads(row.genres.replace("'", '"'))],
                'distance': float(val[1]),
                'more_info': clean({
                    **full_movie.drop(['genres', 'id', 'title'])
                })
            })
        return sorted(
            movies,
            key=lambda d: (d['distance'], d['no_of_ratings'], -d['rating']),
            reverse=True,
        )[:n_recommendations]


if __name__ == '__main__':
    from pprint import pprint
    from tqdm import tqdm
    user_id = 50
    recommender = CollaborativeFilter()
    # movies = recommender.recommend_movies_item_similarity(user_id, n_recommendations=10)
    # pprint(movies)
    # movies = recommender.recommend_KNN(user_id=user_id,  n_recommendations=10)
    # movies = recommender.recommend_KNN(movie_name="Jumanji",  n_recommendations=10)
    movies = list(set(list(recommender.movies_df['title'])))
    print(len(movies))
    valid_movies = []
    for movie in tqdm(movies):
        try:
            recommender.recommend_movies_item_similarity(movie_name=movie, n_recommendations=10)
            valid_movies.append(movie)
        except Exception as e:
            pass
    np.savez_compressed("valid_movies.npz", valid_movies)
    print(f"{len(movies) - len(valid_movies)} failed")
    # 42277

    # pprint(movies)
