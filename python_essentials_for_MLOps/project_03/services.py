"""
services file of predicting insurance costs
Author: Guilherme Pablo de Santana Maciel
Date: 2023-10-07
"""
import logging
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from tabulate import tabulate


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
    table = tabulate(dataframe.head(10), headers='keys',
                     tablefmt='pretty', showindex=False)
    print(table)

def read_dataset(file_path:str) -> pd.DataFrame:
    """
    Reads the dataset from the given file path.

    Args:
        file_path (str): The path to the dataset file.

    Returns:
        pd.DataFrame: The loaded dataset as a DataFrame.
    """
    try:
        logging.info("Reading the dataset")
        insurance_df = pd.read_csv(file_path)
        return insurance_df
    except FileNotFoundError:
        logging.error("Dataset file not found")
        raise

def transform_data(insurance_df:pd.DataFrame) -> pd.DataFrame:
    """
    Transform the 'charges' column of the DataFrame to log2.

    Args:
        insurance_df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with the 'log_charges' column added.

    Raises:
        KeyError: If the 'charges' column is not found in the dataset.

    """
    try:
        logging.info("Transforming the 'charges' column to log2")
        insurance_df["log_charges"] = np.log2(insurance_df["charges"])
        return insurance_df
    except KeyError:
        logging.error("Column 'charges' not found in the dataset")
        raise

def split_data(insurance_df: pd.DataFrame) -> list:
    """
    Split the dataset into training and test sets.

    Args:
        insurance_df (pd.DataFrame): The DataFrame containing insurance data.

    Returns:
        list: A list containing X_train, X_test, y_train, and y_test.
    """
    try:
        logging.info("Splitting the data into training and test sets")
        insurance_df["is_smoker"] = insurance_df["smoker"] == "yes"
        feature_matrix = insurance_df[["age", "bmi", "is_smoker"]]
        target_variable = insurance_df["log_charges"]
        x_train, x_test, y_train, y_test = train_test_split(feature_matrix,
                                                            target_variable,
                                                            test_size=0.25,
                                                            random_state=1)
        return x_train, x_test, y_train, y_test
    except KeyError:
        logging.error("Columns 'age', 'bmi', 'smoker', or 'log_charges' not found in the dataset")
        raise

def train_model(x_train: pd.DataFrame, y_train) -> LinearRegression:
    """
    Train a linear regression model.

    Args:
        X_train (DataFrame or array-like): Training data features.
        y_train (Series or array-like): Training data target variable.

    Returns:
        LinearRegression: Trained linear regression model.

    Raises:
        Exception: If there is an error during model training.
    """
    try:
        logging.info("Training the linear regression model")
        insurance_model = LinearRegression()
        insurance_model.fit(x_train, y_train)
        return insurance_model
    except Exception as exception:
        logging.error("Error training the model: %s",str(exception))
        raise

def evaluate_model(insurance_model, x_train, y_train, x_test, y_test):
    """
    Evaluate the performance of a machine learning model on training and test sets.

    Parameters:
    - model: The trained machine learning model.
    - X_train: The feature matrix of the training set.
    - y_train: The target variable of the training set.
    - X_test: The feature matrix of the test set.
    - y_test: The target variable of the test set.

    Returns:
    - mse_test_original_scale: Mean Squared Error (MSE) on the test set in the original scale.
    """
    try:
        logging.info("Evaluating model performance on the training set")
        y_pred_train = insurance_model.predict(x_train)
        mse_train = mean_squared_error(y_train, y_pred_train)
        logging.info("MSE on the training set (log-terms): %s", str(mse_train))
        mse_train_original_scale = np.exp(mse_train)
        logging.info("MSE on the training set (original scale): %s",str(mse_train_original_scale))

        logging.info("Calculating the coefficient of determination (R-squared) on the training set")
        r2_train = r2_score(y_train, y_pred_train)
        logging.info("R-squared on the training set: %s",str(r2_train))
        non_intercept_coefficients = insurance_model.coef_

        logging.info("Getting the non-intercept coefficients: %s", non_intercept_coefficients)

        logging.info("Evaluating model performance on the test set")
        y_pred_test = insurance_model.predict(x_test)
        mse_test = mean_squared_error(y_test, y_pred_test)
        logging.info("MSE on the test set (log-terms): %s", str(mse_test))
        mse_test_original_scale = np.exp(mse_test)
        logging.info("MSE on the test set (original scale): %s", str(mse_test_original_scale))

        return mse_test_original_scale
    except Exception as exception:
        logging.error("Error evaluating the model: %s", str(exception))
        raise
