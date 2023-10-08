"""
Test cases for the insurance functions.
"""
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from services import (
    read_dataset,
    transform_data,
    split_data,
    train_model,
    evaluate_model,
)

def test_read_dataset():
    """
    Test the 'read_dataset' function.

    This test function creates a temporary CSV file with test data,
    reads it using the 'read_dataset' function,
    and asserts that the result is a pandas DataFrame.
    It also cleans up by removing the temporary test file.

    """
    # Create a temporary test CSV file for testing
    test_data = {
        'age': [25, 30, 35],
        'bmi': [22.5, 24.0, 26.5],
        'charges': [1000, 1200, 1500]}
    test_df = pd.DataFrame(test_data)
    test_df.to_csv('test_insurance.csv', index=False)

    # Test reading the dataset
    file_path = 'test_insurance.csv'
    data_test_df = read_dataset(file_path)
    assert isinstance(data_test_df, pd.DataFrame)

    # Clean up: remove the temporary test file
    os.remove('test_insurance.csv')

def test_transform_data():
    """
    Test the transform_data function.
    This test checks if the transform_data function correctly adds
    the 'log_charges' column to the DataFrame.

    """
    # Create a test DataFrame
    test_data = {'charges': [1000, 1200, 1500]}
    test_df = pd.DataFrame(test_data)

    # Test transforming data
    transformed_df = transform_data(test_df)
    assert 'log_charges' in transformed_df.columns

def test_split_data():
    """
    Test the split_data function.

    This function creates a test DataFrame, calls the split_data function,
    and asserts that the returned values have the correct data types.

    Args:
        None

    Returns:
        None
    """
    # Create a test DataFrame
    test_data = {
        'age': [25, 30, 35],
        'bmi': [22.5, 24.0, 26.5],
        'smoker': ['yes', 'no', 'yes'],
        'log_charges': [6.9, 7.1, 7.3]}
    test_df = pd.DataFrame(test_data)

    # Test splitting data
    x_train, x_test, y_train, y_test = split_data(test_df)
    assert isinstance(x_train, pd.DataFrame)
    assert isinstance(x_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)

def test_train_model():
    """
    Test the train_model function.

    This function checks if the train_model function correctly trains a linear regression model
    using the provided training data.

    """
    # Create a test DataFrame
    test_data = {
        'age': [25, 30, 35],
        'bmi': [22.5, 24.0, 26.5],
        'smoker': ['yes', 'no', 'yes'],
        'log_charges': [6.9, 7.1, 7.3]}
    test_df = pd.DataFrame(test_data)

    # Split the data
    x_train, _, y_train, _ = split_data(test_df)

    # Test training the model
    model = train_model(x_train, y_train)
    assert isinstance(model, LinearRegression)

def test_evaluate_model():
    """
    Test the evaluate_model function.

    This function creates a test DataFrame, splits the data, trains the model,
    and evaluates the model's performance. It checks whether the result is of
    the correct data type.

    Returns:
        None
    """
    # Create a test DataFrame
    test_data = {'age': [25, 30, 35],
                 'bmi': [22.5, 24.0, 26.5],
                 'smoker': ['yes', 'no', 'yes'],
                 'log_charges': [6.9, 7.1, 7.3]}
    test_df = pd.DataFrame(test_data)

    # Split the data
    x_train, x_test, y_train, y_test = split_data(test_df)

    # Train the model
    model = train_model(x_train, y_train)

    # Test evaluating the model
    mse_test_original_scale = evaluate_model(model, x_train, y_train, x_test, y_test)
    assert isinstance(mse_test_original_scale, float)
