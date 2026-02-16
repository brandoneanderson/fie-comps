from paths import *
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score,
    precision_recall_curve
)

'''
    Main file for loading in data, creating model, and training model
'''

if __name__ == "__main__":
    TRAINING_CSV = "/Users/ishapatel/COMPS/fie-comps/ML/datasets/training.csv"

    # Load in dataframe
    ext_dataset_csv_df = pd.read_csv(TRAINING_CSV)

    # Drop ext names
    ext_dataset_csv_df = ext_dataset_csv_df.drop('Extension Name', axis = 1)

    # Checking each column feature, cvs is nasty
    print(ext_dataset_csv_df.columns)

    # Split dataset into features and labels
    # X = ext_dataset_csv_df.loc[:, 'All http domains':'num_object_tags']
    # X = X.fillna(0)
    # # y = ext_dataset_csv_df.loc[:, 'label':'label']
    # y = ext_dataset_csv_df['label']
    # Split dataset into features and labels
    y = ext_dataset_csv_df["label"].astype(int)

    # Everything except label is a feature (much safer than slicing)
    feature_cols = [c for c in ext_dataset_csv_df.columns if c != "label"]

    X = ext_dataset_csv_df[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)


    # Split dataset into X_train, y_train, X_test, Y_test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # See if shapes match expected output
    print('Training data shape: ', X_train.shape)
    print('Training labels shape: ', y_train.shape)
    print('Test data shape: ', X_test.shape)
    print('Test labels shape: ', y_test.shape)

    # 4) Pipeline: scale then SVM-RBF
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=42))
    ])

    # 5) Hyperparameter tuning
    param_grid = {
        "svm__C": [0.1, 1, 10, 100, 1000],
        "svm__gamma": [1e-4, 1e-3, 1e-2, 1e-1, "scale"],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    gs = GridSearchCV(
        pipe,
        param_grid=param_grid,
        scoring="f1",   
        cv=cv,
        n_jobs=-1,
        verbose=2
    )

    gs.fit(X_train, y_train)
    best_model = gs.best_estimator_
    print("Best params:", gs.best_params_)
    print("Best CV score:", gs.best_score_)

    # 6) Evaluate on test
    proba = best_model.predict_proba(X_test)[:, 1]
    pred_05 = (proba >= 0.5).astype(int)

    print("\n=== Test @ threshold 0.5 ===")
    print("ROC-AUC:", roc_auc_score(y_test, proba))
    print("PR-AUC:", average_precision_score(y_test, proba))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_05))
    print(classification_report(y_test, pred_05, digits=3))

    # 7) Choose best threshold by max F1 (optional but good)
    precision, recall, thresholds = precision_recall_curve(y_test, proba)
    f1_scores = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    best_i = int(np.argmax(f1_scores))
    best_thresh = float(thresholds[best_i])

    pred_best = (proba >= best_thresh).astype(int)
    print("\n=== Test @ threshold chosen by max F1 ===")
    print("Chosen threshold:", best_thresh)
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_best))
    print(classification_report(y_test, pred_best, digits=3))

    # 8) Save model bundle
    bundle = {
        "model": best_model,
        "feature_cols": feature_cols,
        "threshold": best_thresh,
        "best_params": gs.best_params_,
    }
    # joblib.dump(bundle, MODEL_BUNDLE_PATH)  # set this in paths.py
    # print(f"Saved model bundle to: {MODEL_BUNDLE_PATH}")

    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA

    # Reduce to 2D
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X_train)

    # Train SVM in 2D space (for visualization only)
    svm_2d = SVC(kernel="rbf", C=gs.best_params_["svm__C"],
                gamma=gs.best_params_["svm__gamma"])
    svm_2d.fit(X_2d, y_train)

    # Create mesh grid
    x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
    y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                        np.linspace(y_min, y_max, 200))

    Z = svm_2d.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.figure(figsize=(8,6))
    plt.contourf(xx, yy, Z, alpha=0.3)
    plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y_train, edgecolors="k", s=20)
    plt.title("SVM-RBF Decision Boundary (PCA Projection)")
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.show()

    from sklearn.metrics import roc_curve

    fpr, tpr, _ = roc_curve(y_test, proba)

    plt.figure()
    plt.plot(fpr, tpr)
    plt.plot([0,1],[0,1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve (AUC = %.3f)" % roc_auc_score(y_test, proba))
    plt.show()

    plt.figure()
    plt.plot(recall, precision)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve (PR-AUC = %.3f)" % average_precision_score(y_test, proba))
    plt.show()

    import seaborn as sns

    cm = confusion_matrix(y_test, pred_best)

    plt.figure()
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Benign", "Malicious"],
                yticklabels=["Benign", "Malicious"])
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.title("Confusion Matrix")
    plt.show()

    from sklearn.inspection import permutation_importance

    result = permutation_importance(best_model, X_test, y_test, n_repeats=10, random_state=42)

    importance = pd.Series(result.importances_mean, index=feature_cols)
    importance = importance.sort_values(ascending=False).head(15)

    plt.figure(figsize=(8,6))
    importance.plot(kind="barh")
    plt.gca().invert_yaxis()
    plt.title("Top 15 Feature Importances (Permutation)")
    plt.show()

    # # Define the SVM gamma parameter range
    # param_range = np.logspace(-3, 3, 7)

    # # Calculate the validation curve for the SVM gamma parameter
    # train_scores, test_scores = validation_curve(SVC(kernel = 'rbf'), X_train, y_train, param_name = "gamma", param_range = param_range, cv = 5, error_score = 'raise')

    # # Calculate the mean and standard deviation of the training and testing scores
    # train_mean = np.mean(train_scores, axis = 1)
    # train_std = np.std(train_scores, axis=1)
    # test_mean = np.mean(test_scores, axis=1)
    # test_std = np.std(test_scores, axis=1)

    # print("train_mean:", train_mean, "train_std:", train_std, "test_mean:", test_mean, "test_std:", test_std)
    # C_range = np.logspace(-2, 10, 13)
    # gamma_range = np.logspace(-9, 3, 13)
    # param_grid = dict(gamma=gamma_range, C=C_range)
    # cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    # grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    # grid.fit(X, y)

    # print(
    #     "The best parameters are %s with a score of %0.2f"
    #     % (grid.best_params_, grid.best_score_)
    # )


    # # Plot the validation curve
    # plt.title("Validation Curve for RBF SVM")
    # plt.xlabel("Gamma")
    # plt.ylabel("Score")
    # plt.ylim(0.0, 1.1)
    # lw = 2
    # plt.semilogx(param_range, train_mean, label="Training score",
    #             color="darkorange", lw=lw)
    # plt.fill_between(param_range, train_mean - train_std,
    #                 train_mean + train_std, alpha=0.2,
    #                 color="darkorange", lw=lw)
    # plt.semilogx(param_range, test_mean, label="Cross-validation score",
    #             color="navy", lw=lw)
    # plt.fill_between(param_range, test_mean - test_std,
    #                 test_mean + test_std, alpha=0.2,
    #                 color="navy", lw=lw)
    # plt.legend(loc="best")
    # plt.show()
