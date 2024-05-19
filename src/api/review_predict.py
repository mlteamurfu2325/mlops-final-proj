import logging
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()


class Review(BaseModel):
    text: str


# Function to load the model and vectorizer
def load_model_and_vectorizer():
    model_path = f"{str(Path(__file__).parent.parent.parent)}/models/logistic_regression_model.pkl"
    vectorizer_path = f"{str(Path(__file__).parent.parent.parent)}/models/tfidf_vectorizer.pkl"

    try:
        model = joblib.load(model_path)
        tfidf = joblib.load(vectorizer_path)
        logging.info("Model and vectorizer loaded successfully")
        return model, tfidf
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise HTTPException(status_code=500, detail="Model or vectorizer file not found")


model, tfidf = load_model_and_vectorizer()


@app.post("/predict/")
async def predict(review: Review):
    if len(review.text) < 2:
        raise HTTPException(status_code=400, detail="Review length is too short")
    if len(review.text) > 10000:
        raise HTTPException(status_code=413, detail="Review length is too large")

    text = review.text
    transformed_text = tfidf.transform([text])
    predicted_rating = model.predict(transformed_text)[0]
    predicted_probabilities = model.predict_proba(transformed_text)[0]

    probability_dict = {
        class_label: round(prob, 2) for class_label, prob in zip(model.classes_, predicted_probabilities)
    }

    return {
        "review_rating_probabilities": probability_dict,
        "additional_data": {"predicted_rating": predicted_rating, "original_text": text},
    }
