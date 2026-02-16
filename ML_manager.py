from parser.paths import *
import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split

'''
    Main file for loading in data, creating model, and training model
'''

if __name__ == "__main__":

    # Load in dataframe
    ext_dataset_csv_df = pd.read_csv(TRAINING_CSV)

    # Checking each column feature, cvs is nasty
    print(ext_dataset_csv_df.columns)

    # Split dataset into features and labels
    X = ext_dataset_csv_df.loc[:, 'All http domains':'num_object_tags']
    y = ext_dataset_csv_df.loc[:, 'label':'label']

    # Split dataset into X_train, y_train, X_test, Y_test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # See if shapes match expected output
    print('Training data shape: ', X_train.shape)
    print('Training labels shape: ', y_train.shape)
    print('Test data shape: ', X_test.shape)
    print('Test labels shape: ', y_test.shape)
