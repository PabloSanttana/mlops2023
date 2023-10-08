"""
main file of predicting insurance costs
Author: Guilherme Pablo de Santana Maciel
Date: 2023-10-07
"""
import logging
import services

# Configurando o nível de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


try:
    FILE_PATH = "./dataset/insurance.csv"
    insurance_df = services.read_dataset(FILE_PATH)
    services.print_dataframe_table(insurance_df)

    insurance_df = services.transform_data(insurance_df)
    services.print_dataframe_table(insurance_df)

    X_train, X_test, y_train, y_test = services.split_data(insurance_df)
    insurance_model = services.train_model(X_train, y_train)
    result_in_original_scale = services.evaluate_model(insurance_model,
                                                       X_train, y_train,
                                                       X_test, y_test)

    logging.info("Final score on the test set: %s", str(result_in_original_scale))
except FileNotFoundError as file_not_found:
    logging.error("File not found: %s", str(file_not_found))
except KeyError as key_error:
    logging.error("Key error: %s", str(key_error))
