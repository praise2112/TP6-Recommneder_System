import numpy as np
import os
import pickle
import pandas as pd
import math

MODEL_PATH = "models"


def clean(dict):
    for key, val in dict.items():
      if type(val) == str:
        dict[key] = val.replace("'", '"')
      try:
        if math.isnan(val):
          dict[key] = None
      except:
        pass
    return dict


class Base:
  """ Base class for our models """

  def __init__(self):
    self.movies_df = self.load('movies_df_cf.npz', as_df=True, columns=['movieId', 'title', 'genres', 'similarity'])
    self.movies_df_full = self.load('movies_df_full.npz', as_df=True)
    self.movies_df_full_cols = self.load('movies_df_full_cols.npz')
    self.movies_df_full.columns = self.movies_df_full_cols.tolist()
    self.valid_movies_itm = self.load("valid_movies_itm.npz")
    self.valid_users_itm = self.load("valid_users_itm.npz")
    self.valid_users_knn = self.load("valid_users_knn.npz")
    self.valid_movies_knn = self.load("valid_movies_knn.npz")

    ## self.valid_users_cb = self.load("valid_users_cb.npz")

    self.valid_movies_cb = self.load("valid_movies_cb.npz")

    self.ratings_df = self.load('ratings_df_cf.npz', as_df=True, columns=['userId', 'movieId', 'rating', 'timestamp'])

  @staticmethod
  def load(file_name, as_df=False, from_pkl=False, **kwargs):
      dir_path = os.path.dirname(os.path.realpath(__file__))
      path = os.path.join(dir_path, MODEL_PATH, file_name)
      if from_pkl:
          with open(path, 'rb') as f:
              return pickle.load(f)
      np_arr = np.load(path,  allow_pickle=True)
      np_arr = np_arr[np_arr.files[0]]
      if as_df:
          np_arr = pd.DataFrame(np_arr, **kwargs)
      return np_arr
