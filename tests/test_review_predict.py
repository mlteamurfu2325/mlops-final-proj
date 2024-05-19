import sys
from pathlib import Path

from fastapi.testclient import TestClient


# Add the root directory to the sys.path before importing any modules
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.api.review_predict import app


client = TestClient(app)


def test_predict_endpoint():
    response = client.post("/predict/", json={"text": "Отличный продукт, очень понравился!"})
    assert response.status_code == 200
    data = response.json()

    assert "review_rating_probabilities" in data
    assert "additional_data" in data
    assert "predicted_rating" in data["additional_data"]
    assert "original_text" in data["additional_data"]
    assert data["additional_data"]["original_text"] == "Отличный продукт, очень понравился!"


def test_predict_empty_text():
    response = client.post("/predict/", json={"text": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Review length is too short"


def test_predict_too_short_text():
    response = client.post("/predict/", json={"text": "A"})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Review length is too short"


def test_predict_too_long_text():
    long_text = "A" * 10001
    response = client.post("/predict/", json={"text": long_text})
    assert response.status_code == 413
    data = response.json()
    assert data["detail"] == "Review length is too large"


def test_predict_bad_review():
    review_text = (
        "Концерт якобы должен длиться 2 часа , в итоге 20 минут прыгали на скакалке , 20 минут клоун раскачивал зал и 20 минут антракт , "
        "еще задержали концерт на 15 минут в итоге , танцевали 45 минут , взяли 2,5 т.р. не стыдно ? Конечно же не стыдно, иначе бы так не делали . "
        "Ролики в интернете гораздо интереснее концерта , Видимо пора на покой Алле Духовой!!!"
    )
    response = client.post("/predict/", json={"text": review_text})
    assert response.status_code == 200
    data = response.json()

    assert "review_rating_probabilities" in data
    assert "additional_data" in data
    assert data["additional_data"]["predicted_rating"] == "bad"


def test_predict_excellent_review():
    review_text = (
        "Очень понравился спектакль. В какой-то момент выключился из реальности и полностью погрузился в происходящее "
        "(давно такого не было, даже забыл про телефон). Актёры играют живо, интересно. Эмоции настоящие. Рекомендую сходить! "
        "Давно не видел такого качественного спектакля!"
    )
    response = client.post("/predict/", json={"text": review_text})
    assert response.status_code == 200
    data = response.json()

    assert "review_rating_probabilities" in data
    assert "additional_data" in data
    assert data["additional_data"]["predicted_rating"] == "excellent"
