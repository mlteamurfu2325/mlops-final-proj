from pathlib import Path

import pandas as pd
import pytest


def check_review_rating_distribution(df):
    rating_counts = df["review_rating"].value_counts(normalize=True)
    assert rating_counts.get("excellent", 0) >= 0.50, "Less than 50% of reviews are rated 'excellent'"
    assert rating_counts.get("great", 0) >= 0.03, "Less than 3% of reviews are rated 'great'"
    assert rating_counts.get("fine", 0) >= 0.02, "Less than 2% of reviews are rated 'fine'"
    assert rating_counts.get("bad", 0) >= 0.01, "Less than 1% of reviews are rated 'bad'"
    assert rating_counts.get("okay", 0) >= 0.01, "Less than 1% of reviews are rated 'okay'"


def check_for_duplicates(df):
    assert df.duplicated().sum() == 0, "There are duplicated rows in the dataset"


def check_non_empty_event_id(df):
    assert df["event_id"].isnull().sum() == 0, "There are rows with missing 'event_id'"


@pytest.fixture
def load_data():
    input_filepath = f"{str(Path(__file__).parent.parent)}/data/processed/processed_reviews.csv"
    return pd.read_csv(input_filepath)


def test_review_rating_distribution(load_data):
    check_review_rating_distribution(load_data)


def test_no_duplicates(load_data):
    check_for_duplicates(load_data)


def test_non_empty_event_id(load_data):
    check_non_empty_event_id(load_data)
