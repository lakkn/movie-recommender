import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def polish_title(title):
  return re.sub("[^a-zA-Z0-9 ]","",title)

def search(title, tfidf, vectorizer, movies):
  title = polish_title(title)
  query = vectorizer.transform([title])
  similarity = cosine_similarity(query,tfidf).flatten()
  indices = np.argpartition(similarity, -5)[-5:]
  results = movies.iloc[indices][::-1]
  return results

def recommend(movie_id, ratings, movies):
  #finding movies where users who like the movie inputed also liked
  similar_users = ratings[(ratings['movieId'] == movie_id) & (ratings['rating'] > 4)]["userId"].unique()
  similar_user_recs = ratings[(ratings['userId'].isin(similar_users)) & (ratings["rating"] > 4)]['movieId']

  #cutting off movies with less than 10% of users liking it
  similar_user_recs = similar_user_recs.value_counts()/len(similar_users)
  similar_user_recs = similar_user_recs[similar_user_recs > 0.1]

  #finding the overall percentage of users who like the movies
  users = ratings[(ratings["movieId"].isin(similar_user_recs.index)) & (ratings["rating"] > 4)]
  users_recs = users["movieId"].value_counts() / len(users["userId"].unique())

  #calculating the score of the recommendation bagsed on overall percentages
  rec_percentages = pd.concat([similar_user_recs, users_recs], axis=1)
  rec_percentages.columns = ["similar","all"]
  
  rec_percentages["score"] = rec_percentages["similar"]/rec_percentages["all"]

  #sorting the scores
  rec_percentages = rec_percentages.sort_values('score', ascending=False)
  return rec_percentages.head(10).merge(movies, left_index=True, right_on="movieId")[['score','title','genres']]

def placeholder(title):
  movies = pd.read_csv("moviedata/movies.csv")
  ratings = pd.read_csv("moviedata/ratings.csv")
  movies["polished_title"] = movies["title"].apply(polish_title)
  vectorizer = TfidfVectorizer(ngram_range=(1,2))
  tfidf = vectorizer.fit_transform(movies["polished_title"])
  searched = search(title,tfidf,vectorizer,movies).head(1)
  print(searched)
  return recommend(searched.iloc[0]['movieId'],ratings,movies)
