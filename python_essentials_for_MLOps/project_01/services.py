"""
services file of Movie Recomendation System
Author: Guilherme Pablo de Santana Maciel
Date: 2023-10-07
"""
import re
import logging
import zipfile
import os
import tqdm
import argparse
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate


# set the logging level
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def get_title_movie() -> str:
    """
    Retrieves the movie title from the command line arguments.

    Returns:
        str: The movie title provided as a command line argument, or 'Unknown' if not provided.
    """
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Movie recommendations")

    # Add an argument named "--movie-title" that expects a string
    parser.add_argument("--movie-title", type=str,
                        help="The title of the movie")

    # Parse the command line arguments
    args = parser.parse_args()

    # Access the value passed for the "--movie-title" argument
    if args.movie_title:
        title_string = args.movie_title
        logging.info("Movie title is: %s", title_string)
    else:
        logging.warning(
            "Warning: Movie title not provided. Using 'Unknown' as default.")
        title_string = "Unknown"

    return title_string


def download_and_extract(url: str, output_dir: str) -> None:
    """
    Download the data from the given URL
    Args:
        url (str): The URL of the data
        output_dir (str): save output dir
    Returns:
        None
    """
    try:
        if not os.path.exists("ml-25m"):
            # Validate the URL and output directory
            if not url.startswith('http'):
                raise ValueError("Invalid URL.")
            if not os.path.isdir(output_dir):
                raise ValueError("Output directory does not exist.")

            # Extract the ZIP file name from the URL
            zip_filename = url.split('/')[-1]
            # Download the file
            
            zip_path = os.path.join(output_dir, zip_filename)

            with requests.Session() as session:  
                response = session.get(url, stream=True,timeout=10)
                total_size = int(response.headers.get('content-length', 0))

                chunk_size = 128 * 1024
                total_chunks = total_size // chunk_size

                with open(zip_filename, 'wb') as file:
                    for data in tqdm.tqdm(response.iter_content(chunk_size=chunk_size),
                                    total=total_chunks,
                                    unit='KB',
                                    desc=zip_filename,
                                    leave=True):
                        file.write(data)

                logging.info("File downloaded to %s", zip_path)

                # Extract the ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                logging.info(
                    "Contents of the file extracted to %s", output_dir)

                # Remove the ZIP file
                os.remove(zip_path)
                logging.info("ZIP file deleted.")

    except requests.exceptions.ConnectionError:
        logging.error("Connection Error")
    except requests.exceptions.Timeout:
        logging.error("Timeout Error")
    except requests.exceptions.HTTPError:
        logging.error("HTTP Error")
    except zipfile.BadZipFile:
        logging.error("The downloaded file is not a valid ZIP file.")


def clean_title_movie(movie_title: str):
    """
    Cleans a movie title by removing special characters and non-alphanumeric characters.

    Args:
        movie_title (str): The movie title to be cleaned.

    Returns:
        str: The cleaned movie title.
    """
    title = re.sub("[^a-zA-Z0-9 ]", "", movie_title)
    return title


def get_similar_movie_titles(
        movie_title: str,
        movies_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Finds similar movie titles based on a given movie title.

    Args:
        movie_title (str): The title of the movie for which you want to find similar titles.
        movies_df (pd.DataFrame): The DataFrame of movie titles.

    Returns:
        pd.DataFrame: A DataFrame containing similar movie titles.

    Raises:
        ValueError: If the cleaned movie title is empty.
    """
    try:
        # instantiate the TF-IDF vectorizer
        logging.info("Instantiating the TF-IDF vectorizer")
        tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 2))

        # fit the vectorizer and transform the data
        logging.info("Fitting and transforming the data")
        tfidf_matrix = tfidf_vectorizer.fit_transform(movies_df["clean_title"])

        clean_title = clean_title_movie(movie_title)

        if not clean_title:
            raise ValueError("Cleaned movie title is empty")
        query_vec = tfidf_vectorizer.transform([clean_title])
        similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
        similarity_movie_indices = similarity.argsort()[-5:][::-1]
        results = movies_df.iloc[similarity_movie_indices].copy()
        return results
    except ValueError as erros:
        logging.error("An error occurred: %s", erros)
        # Return an empty DataFrame as a default result.
        return pd.DataFrame()


def print_dataframe_table(dataframe, columns=None):
    """
    Prints a DataFrame table.

    Args:
        dataframe (pd.DataFrame): The DataFrame to be printed.
        columns (list or None, optional): A list of column names to include in the table. 
            If None, all columns are included. Default is None.

    Returns:
        None
    """
    if columns is not None:
        dataframe = dataframe[columns]

    # Convert the DataFrame to a formatted table
    table = tabulate(dataframe, headers='keys',
                     tablefmt='pretty', showindex=False)
    print(table)


def discover_similar_movies(
        movies_df: pd.DataFrame,
        ratings_df: pd.DataFrame,
        movie_title: str) -> pd.DataFrame:
    """
    Finds similar movies based on user ratings.

    Args:
        movies_df (pd.DataFrame): The DataFrame of movies.
        ratings_df (pd.DataFrame): The DataFrame of user ratings.
        movie_title (str): The title of the movie for which you want to find similar movies.

    Returns:
        pd.DataFrame: A DataFrame containing the recommended similar movies.
    """
    try:
        # Get movie ID
        movie_id = movies_df.loc[movies_df["title"]
                                 == movie_title, "movieId"].values[0]

        logging.info("Got movie ID: %s", movie_id)

        # Find similar users who rated the movie highly
        similar_users = ratings_df[(ratings_df["movieId"] == movie_id) &
                                   (ratings_df["rating"] > 4)]["userId"].unique()

        logging.info("Found %d similar users", len(similar_users))

        # Find movies highly rated by similar users
        similar_user_recs = ratings_df[(ratings_df["userId"].isin(similar_users)) &
                                       (ratings_df["rating"] > 4)]["movieId"]
        similar_user_recs = similar_user_recs.value_counts() / len(similar_users)
        similar_user_recs = similar_user_recs[similar_user_recs > 0.10]

        logging.info(
            "Found %d highly recommended movies by similar users", len(similar_user_recs))

        # Find all users who rated the highly recommended movies
        all_users = ratings_df[(ratings_df["movieId"].isin(similar_user_recs.index))
                               & (ratings_df["rating"] > 4)]
        # Calculate recommendation percentages
        all_user_recs = all_users["movieId"].value_counts(
        ) / len(all_users["userId"].unique())
        rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
        rec_percentages.columns = ["similar", "all"]
        rec_percentages["score"] = rec_percentages["similar"] / \
            rec_percentages["all"]
        rec_percentages = rec_percentages.sort_values("score", ascending=False)

        logging.info("Calculated recommendation percentages")

        # Merge with movie information and return the top 10 recommendations
        top_recommendations = rec_percentages.head(10).merge(
            movies_df,
            left_index=True,
            right_on="movieId")
        return top_recommendations
    except ValueError as error:
        # Lide com a exceção ValueError de forma específica
        logging.error("An error occurred: %s", error)
        return pd.DataFrame()
