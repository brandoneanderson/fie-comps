from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, f1_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import matplotlib.pyplot as plt
import numpy as np

# Paper guide
'''
    1. Optimize the number of trees in the forest that is used to contruct the RF
        a. Done with Out-of-bag error (which calculates the misclassification probability for out-of-bag observations in the training set)
        b. varying number of trees from 10 to 300 (they found 250 to be perfect for them)
    
    2. Run RF with optimized number of trees to calcultae importance score for each feature
        a. Calculate the importance score of each of the n features, where n = 51
        b. Rank the n features by the importance score in decreasing order
        c. Apply the first k features to the RF classifer, for k = 1 to n, and select the features involved
            in the classifier producing the lowest mean absolute error (MAE)
    
    OUTPUT: k features producing lowest MAE (mean absolute error)

    NOT DONE HERE, BUT WHAT WE DO WITH OUTPUT
    3. Feed features into SVM-RBF
'''

def randomForest(X, y):
    # Grab optimal tree count
    tree_count = compute_optimized_tree_count(X, y)

    # Grab optimal k best features using k-fold to avoid data leakage
    best_k_features_size, error_scores = find_best_k_features_kfold(X, y, tree_count)

    # Grab k-best features on entire dataset

    print("Best k feature size:", best_k_features_size)
    print("Error scores:", error_scores)
    print("Best error score:", error_scores[best_k_features_size])

    # Plot MAE vs number of selected features
    plt.plot(range(1, len(error_scores)+1), error_scores)
    plt.xlabel("Number of Features")
    plt.ylabel("Cross-Validated MAE")
    plt.title("MAE vs Number of Selected Features")
    plt.show()

    optimized_features = get_top_k_features(X, y, tree_count, best_k_features_size)

    return optimized_features

def compute_optimized_tree_count(X, y):
    '''
        Purpose: Find optimal number of trees to construct our RF
        Why this works: OOB error, calculates the misclassification prob. for out-of-bag
                        observations in the training set. Get lowest error
    '''
    # Set up params
    min_trees = 15
    max_trees = 300
    trees_range = range(min_trees, max_trees + 1, 10)
    oob_errors = []

    # Loop through each tree count and find OOB
    for n_tree in trees_range:
        # Create a random forest for given tree count, record OOB score
        rf = RandomForestClassifier(n_estimators = n_tree, oob_score = True, bootstrap = True, random_state = 42, n_jobs = -1)
        rf.fit(X, y)

        oob_error = 1 - rf.oob_score_
        oob_errors.append(oob_error)

    # Find best tree count that minimizes OOB
    best_trees = trees_range[oob_errors.index(min(oob_errors))]
    print(f"Optimal number of trees based on OOB error: {best_trees}")

    # Plot results to find where error stabilizes
    # plt.plot(trees_range, oob_errors)
    # plt.xlabel("Number of Trees (n_estimators)")
    # plt.ylabel("OOB Error Rate")
    # plt.title("OOB Error Rate vs. Number of Trees")
    # plt.show()

    return best_trees

def find_best_k_features_kfold(X, y, tree_count):
    error_scores = []

    # Ensure each fold contains same percentage of samples for each class as the complete dataset
    skf = StratifiedKFold(n_splits = 5, shuffle = True, random_state = 42)

    # number of columns in the dataset
    n_features = X.shape[1]

    # Iterate through diff sized subsets of features
    for feature_subset_size in range(1, n_features + 1):
        fold_errors = []

        # Create train and val data for each fold
        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            # Train rf only on training fold
            rf = RandomForestClassifier(n_estimators=tree_count,random_state=42,n_jobs=-1)
            rf.fit(X_train, y_train)

            # Rank features inside fold
            importances = rf.feature_importances_
            ranked_features = np.argsort(importances)[::-1]

            # Best k-features in this fold
            selected_features = ranked_features[:feature_subset_size]

            # retrain using only top-k
            rf_k = RandomForestClassifier(n_estimators=tree_count,random_state=42,n_jobs=-1)
            rf_k.fit(X_train.iloc[:, selected_features], y_train)

            # Store predictions
            preds = rf_k.predict(X_val.iloc[:, selected_features])

            # Store MAE errors for each fold
            fold_errors.append(mean_absolute_error(y_val, preds))

        # Append average of fold errors
        error_scores.append(np.mean(fold_errors))
    
    # Grab optimal k features that return lowest score
    optimal_k = np.argmin(error_scores) + 1

    return optimal_k, error_scores

def get_top_k_features(X, y, tree_count, k):
    rf = RandomForestClassifier(n_estimators = tree_count, random_state = 42, n_jobs = -1)
    rf.fit(X,y)

    # Get feature importances
    importances = rf.feature_importances_

    # Order them in descending order
    ranked_indices = np.argsort(importances)[::-1]

    # select top-k indices
    top_k_indices = ranked_indices[:k]

    # Get feature names of top-k indices
    top_k_feature_names = X.columns[top_k_indices]

    return top_k_feature_names