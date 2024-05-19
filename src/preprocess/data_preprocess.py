import logging
from pathlib import Path

import pandas as pd


def preprocess_data(filepath):
    df = pd.read_csv(filepath, delimiter=";")
    df = df[df["review_rating"] != "Без оценки"].copy()
    ratings_ru_en = {
        "Великолепно": "excellent",
        "Отлично": "great",
        "Хорошо": "fine",
        "Нормально": "okay",
        "Плохо": "bad",
    }
    df["review_rating"] = df["review_rating"].map(ratings_ru_en)

    if df.isnull().sum().any():
        logging.warning("Missing values detected. Dropping missing values.")
        df.dropna(inplace=True)

    # Remove duplicates
    initial_row_count = len(df)
    df.drop_duplicates(inplace=True)
    final_row_count = len(df)
    logging.info(f"Removed {initial_row_count - final_row_count} duplicate rows.")

    return df


def save_processed_data(df, output_path):
    # Ensure the target directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    logging.info(f"Processed data saved to {output_path}")


if __name__ == "__main__":
    input_filepath = f"{str(Path(__file__).parent.parent.parent)}/data/raw/reviews.csv"
    output_filepath = f"{str(Path(__file__).parent.parent.parent)}/data/processed/processed_reviews.csv"

    df = preprocess_data(input_filepath)
    save_processed_data(df, output_filepath)
