"""
Main file of Movie Recomendation System
Author: Guilherme Pablo de Santana Maciel
Date: 2023-10-7
"""
# import libraries
import logging
import os
import sys
import pandas as pd
import services


URL = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
script_path = os.path.abspath(__file__)
base_directory = os.path.dirname(script_path)


title_movie = services.get_title_movie()
if title_movie == "Unknown":
    sys.exit()

services.download_and_extract(URL, base_directory)


# import data from moveis
logging.info("set data movies")
# Construct the path to the movies.csv file
movies_csv_path = os.path.join(base_directory, "ml-25m", "movies.csv")

movies_df = pd.read_csv(movies_csv_path)

# log the shape of the data
logging.info("The shape of the data is %s", movies_df.shape)

# clean the movie title
logging.info("Cleaning the movie title")
movies_df["clean_title"] = movies_df["title"].apply(services.clean_title_movie)

# get the most similar movies
logging.info("Getting the most similar movies to %s", title_movie)
results = services.get_similar_movie_titles(title_movie, movies_df)


# print the results
columns_to_include = ["title", "genres"]
services.print_dataframe_table(results, columns_to_include)

ratings_csv_path = os.path.join(base_directory, "ml-25m", "ratings.csv")
# read the ratings data

logging.info("loading csv ratings")

ratings_df = pd.read_csv(ratings_csv_path)

logging.info("Finding similar by user ratings")

# Get the first movie title from 'results'
first_movie_title = results.iloc[0]["title"]

top_recommendations_movies = services.discover_similar_movies(
    movies_df,
    ratings_df,
    first_movie_title
)

if top_recommendations_movies.empty:
    logging.warning("o similar movies were found.")
else:
    columns_to_include = ["title", "genres"]
    services.print_dataframe_table(
        top_recommendations_movies, columns_to_include)
