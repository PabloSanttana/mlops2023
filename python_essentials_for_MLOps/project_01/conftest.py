"""
Test file to define fixtures of Movie Recomendation System
Author: Guilherme Pablo de Santana Maciel
Date: 2023-09-26
"""
# import libraries
import os
import pytest
import pandas as pd
from services import download_and_extract


@pytest.fixture
def load_input_data() -> tuple:
    """
    Load the input data

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Tuple of DataFrames
    """
    # import the data
    if os.path.exists("ml-25m"):
        movies_df = pd.read_csv("ml-25m/movies.csv")
        ratings_df = pd.read_csv("ml-25m/ratings.csv")
    else:
        url = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
        script_path = os.path.abspath(__file__)


        base_directory = os.path.dirname(script_path)
        download_and_extract(url,base_directory)

    return movies_df, ratings_df
