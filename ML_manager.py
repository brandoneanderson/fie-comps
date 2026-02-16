from parser.paths import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, validation_curve
from sklearn.svm import SVC

'''
    Main file for loading in data, creating model, and training model
'''

if __name__ == "__main__":

    # Load in dataframe
    ext_dataset_csv_df = pd.read_csv(TRAINING_CSV)

    # Drop ext names
    ext_dataset_csv_df = ext_dataset_csv_df.drop('Extension Name', axis = 1)

    # Checking each column feature, cvs is nasty
    print(ext_dataset_csv_df.columns)

    # Split dataset into features and labels
    X = ext_dataset_csv_df.loc[:, 'All http domains':'num_object_tags']
    X = X.fillna(0)
    # y = ext_dataset_csv_df.loc[:, 'label':'label']
    y = ext_dataset_csv_df['label']

    # Split dataset into X_train, y_train, X_test, Y_test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # See if shapes match expected output
    print('Training data shape: ', X_train.shape)
    print('Training labels shape: ', y_train.shape)
    print('Test data shape: ', X_test.shape)
    print('Test labels shape: ', y_test.shape)

    # Define the SVM gamma parameter range
    param_range = np.logspace(-3, 3, 7)

    # Calculate the validation curve for the SVM gamma parameter
    train_scores, test_scores = validation_curve(SVC(kernel = 'rbf'), X_train, y_train, param_name = "gamma", param_range = param_range, cv = 5, error_score = 'raise')

    # Calculate the mean and standard deviation of the training and testing scores
    train_mean = np.mean(train_scores, axis = 1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    print("train_mean:", train_mean, "train_std:", train_std, "test_mean:", test_mean, "test_std:", test_std)
    C_range = np.logspace(-2, 10, 13)
    gamma_range = np.logspace(-9, 3, 13)
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    grid.fit(X, y)

    print(
        "The best parameters are %s with a score of %0.2f"
        % (grid.best_params_, grid.best_score_)
    )


    # Plot the validation curve
    plt.title("Validation Curve for RBF SVM")
    plt.xlabel("Gamma")
    plt.ylabel("Score")
    plt.ylim(0.0, 1.1)
    lw = 2
    plt.semilogx(param_range, train_mean, label="Training score",
                color="darkorange", lw=lw)
    plt.fill_between(param_range, train_mean - train_std,
                    train_mean + train_std, alpha=0.2,
                    color="darkorange", lw=lw)
    plt.semilogx(param_range, test_mean, label="Cross-validation score",
                color="navy", lw=lw)
    plt.fill_between(param_range, test_mean - test_std,
                    test_mean + test_std, alpha=0.2,
                    color="navy", lw=lw)
    plt.legend(loc="best")
    plt.show()
