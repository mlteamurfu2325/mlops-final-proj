from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train_model(X_train, y_train):
    """Train a logistic regression model."""
    model = LogisticRegression(multi_class="multinomial", solver="lbfgs", max_iter=500)
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    input_filepath = f"{str(Path(__file__).parent.parent.parent)}/data/processed/processed_reviews.csv"
    df = pd.read_csv(input_filepath)

    X_train, X_test, y_train, y_test = train_test_split(
        df["review_text"], df["review_rating"], test_size=0.2, random_state=42
    )

    tfidf = TfidfVectorizer(max_features=5000)
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    model = train_model(X_train_tfidf, y_train)

    # Save the model and the vectorizer
    model_output_path = f"{str(Path(__file__).parent.parent.parent)}/models/logistic_regression_model.pkl"
    vectorizer_output_path = f"{str(Path(__file__).parent.parent.parent)}/models/tfidf_vectorizer.pkl"

    joblib.dump(model, model_output_path)
    joblib.dump(tfidf, vectorizer_output_path)

    print(f"Model saved to {model_output_path}")
    print(f"Vectorizer saved to {vectorizer_output_path}")
