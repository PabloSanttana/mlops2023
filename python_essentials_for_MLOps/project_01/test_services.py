"""
Movie Recommendation System Services

This module contains functions to download, extract, 
and process data related to movies in the movie recommendation system.
"""
import services

# Test case for a movie title with special characters


def test_clean_title_movie_with_special_characters() -> None:
    """
    Test if the clean_title_movie function correctly 
    removes non-alphanumeric characters from the movie title.
    """
    movie_title = "The $Avengers: Age of Ultron!"
    cleaned_title = services.clean_title_movie(movie_title)
    assert cleaned_title == "The Avengers Age of Ultron"

# Test case for a movie title with non-alphanumeric characters


def test_clean_title_movie_with_non_alphanumeric_characters() -> None:
    """
    Test if the clean_title_movie function correctly 
    removes non-alphanumeric characters from the movie title.

    """
    movie_title = "Pulp Fiction (1994)"
    cleaned_title = services.clean_title_movie(movie_title)
    assert cleaned_title == "Pulp Fiction 1994"


# Test case for an empty movie title
def test_columns_type_of_input_data(load_input_data) -> None:
    """
    Test the data types of columns in the input data.

    Args:
        load_input_data: A fixture that loads the input data as DataFrames.

    Returns:
        None
    """
    movies_df, ratings_df = load_input_data
    assert movies_df["movieId"].dtype == "int64"
    assert movies_df["title"].dtype == "object"
    assert movies_df["genres"].dtype == "object"
    assert ratings_df["userId"].dtype == "int64"
    assert ratings_df["movieId"].dtype == "int64"
    assert ratings_df["rating"].dtype == "float64"
    assert ratings_df["timestamp"].dtype == "int64"

# Test case for a cleaned movie title with special characters


def test_get_similar_movie_titles_with_special_characters(load_input_data) -> None:
    """
    Test function for get_similar_movie_titles with a movie title containing special characters.

    Args:
        load_input_data: A fixture that loads input data (movies_df, ratings_df) for testing.

    Returns:
        None
    """
    movies_df, _ = load_input_data
    movie_title = "Pulp Fiction (1994)"
    similar_movies = services.get_similar_movie_titles(movie_title, movies_df)
    assert len(similar_movies) >= 1
    assert similar_movies.iloc[0]["clean_title"] == "Pulp Fiction 1994"

# Test case for an empty movie title


def test_get_similar_movie_titles_with_empty_title(load_input_data) ->None:
    """
    Test the behavior of get_similar_movie_titles with an empty movie title.

    Args:
        load_input_data: A fixture that loads input data for testing.
        This test case checks if the function returns an empty DataFrame 
        when given an empty movie title.

    return: 
          None
    """
    movie_title = ""
    movies_df, _ = load_input_data
    similar_movies = services.get_similar_movie_titles(movie_title, movies_df)
    assert len(similar_movies) == 0
