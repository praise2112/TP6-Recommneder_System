import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS
from inference_collaborative import CollaborativeFilter
from inference_content_based import ContentBasedFilter, str2bool
import traceback
from fuzzywuzzy import process
import json
from flask import render_template
import os


collaborative_filter_recommender = CollaborativeFilter()
content_based_filter_recommender = ContentBasedFilter()

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_url_path='', static_folder=os.path.join(dir_path, '..', 'client/build'), template_folder=os.path.join(dir_path, '..', 'client/build'))
app.config['JSON_SORT_KEYS'] = False
CORS(app)


@app.route('/')
def react_app():
  dir_path = os.path.dirname(os.path.realpath(__file__))
  print(os.path.exists(os.path.join(dir_path, '..', 'client', 'build', 'index.html')))
  return render_template('index.html')


@app.route('/collaborative/<path:text>', methods=['GET'])
def predict_collaborative(text):
  try:
    recommender_type = request.args.get("model", default='', type=str)  # get model type from query
    no_of_recommendation = request.args.get("num", default=10, type=int)  # get num of recommendations from query
    is_user = request.args.get("user", default='false', type=str)  # get num of recommendations from query
    is_user = bool(str2bool(is_user))
    kwargs = {"n_recommendations": no_of_recommendation}
    if is_user:
      kwargs['user_id'] = int(text)
    else:
      kwargs['movie_name'] = text
    print(text)

    if recommender_type == 'KNN':
      result = collaborative_filter_recommender.recommend_KNN(**kwargs)
    else:
      result = collaborative_filter_recommender.recommend_movies_item_similarity(**kwargs)
    return jsonify({"success": True,  "prediction": result, "userId" if is_user else "movieName": text })
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong"})


@app.route('/contentbased/<path:text>', methods=['GET'])
def predict_content_based(text):
  try:
    no_of_recommendation = request.args.get("num", default=10, type=int)  # get num of recommendations from query
    result = content_based_filter_recommender.recommend_content_based(text, n_recommendations=no_of_recommendation)
    return jsonify({"success": True,  "prediction": result})
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong",  "movieName": text})


@app.route('/movies/contentbased', methods=['GET'])
def get_content_based_movies():
  try:
    return jsonify({"success": True,  "movies": list(collaborative_filter_recommender.valid_movies_cb)})
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong"})


@app.route('/movies/collaborative', methods=['GET'])
def get_collaborative_movies():
  try:
    recommender_type = request.args.get("model", default='', type=str)  # get model type from query
    valid_movies = collaborative_filter_recommender.valid_movies_knn if recommender_type == "KNN" else collaborative_filter_recommender.valid_movies_itm
    return jsonify({"success": True,  "movies": list(valid_movies)})
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong"})


@app.route('/users/collaborative', methods=['GET'])
def get_collaborative_users():
  try:
    recommender_type = request.args.get("model", default='', type=str)  # get model type from query
    valid_users = collaborative_filter_recommender.valid_users_knn if recommender_type == "KNN" else collaborative_filter_recommender.valid_users_itm
    return jsonify({"success": True, "users": [int(i) for i in list(valid_users)]})
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong"})


@app.route('/movies/<path:text>', methods=['GET'])
def get_movie(text):
  try:
    text = process.extractOne(text, collaborative_filter_recommender.movies_df['title'])[0]
    movie = collaborative_filter_recommender.movies_df_full[collaborative_filter_recommender.movies_df_full['title'] == text].iloc[0].to_dict()
    movie['genres'] = [genre['name'] for genre in json.loads(movie['genres'].replace("'", '"'))]
    return jsonify({"success": True,  "movie": movie })
  except Exception as e:
    traceback.print_exc()
    print(e)
    return jsonify({"success": False,  "info": "Something went wrong"})




if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--port', type=int, nargs='?', const=1, help='sever port', default=80)
  args = parser.parse_args()
  app.run(host='0.0.0.0', debug=True, port=args.port)
