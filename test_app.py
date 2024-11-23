import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Тесты функциональности
def test_valid_data(client):
    valid_data = {
        "data": [
            {"presentation": 8, "materials": 9, "knowledge": 7, "communication": 10},
            {"presentation": 7, "materials": 8, "knowledge": 9, "communication": 9},
            {"presentation": 9, "materials": 7, "knowledge": 8, "communication": 10}
        ],
        "weights": {
            "presentation": 0.25,
            "materials": 0.25,
            "knowledge": 0.25,
            "communication": 0.25
        },
        "value_range": {"min": 1, "max": 10}
    }
    response = client.post('/calculate-rating', json=valid_data)
    assert response.status_code == 200
    assert "final_rating" in response.json

# Тесты на крайовые случаи
def test_min_max_values(client):
    data = {
        "data": [
            {"presentation": 1, "materials": 1, "knowledge": 1, "communication": 1},
            {"presentation": 10, "materials": 10, "knowledge": 10, "communication": 10}
        ],
        "weights": {
            "presentation": 0.25,
            "materials": 0.25,
            "knowledge": 0.25,
            "communication": 0.25
        },
        "value_range": {"min": 1, "max": 10}
    }
    response = client.post('/calculate-rating', json=data)
    assert response.status_code == 200

def test_empty_data(client):
    data = {
        "data": [],
        "weights": {"presentation": 0.5, "materials": 0.5},
        "value_range": {"min": 1, "max": 10}
    }
    response = client.post('/calculate-rating', json=data)
    assert response.status_code == 400

# Тесты на валидацию данных
def test_invalid_weights(client):
    data = {
        "data": [
            {"presentation": 8, "materials": 9, "knowledge": 7, "communication": 10}
        ],
        "weights": {
            "presentation": 0.5,
            "materials": 0.5,
            "knowledge": 0.5,  # Неверная сумма весов
            "communication": 0.5
        },
        "value_range": {"min": 1, "max": 10}
    }
    response = client.post('/calculate-rating', json=data)
    assert response.status_code == 400

# Тесты универсальности
def test_general_domain(client):
    data = {
        "data": [
            {"quality": 9, "design": 8, "functionality": 7}
        ],
        "weights": {
            "quality": 0.4,
            "design": 0.3,
            "functionality": 0.3
        },
        "value_range": {"min": 1, "max": 10}
    }
    response = client.post('/calculate-rating', json=data)
    assert response.status_code == 200
    assert "final_rating" in response.json

# Тесты на воспроизводимость результатов
def test_repeatability(client):
    data = {
        "data": [
            {"presentation": 8, "materials": 9, "knowledge": 7, "communication": 10}
        ],
        "weights": {
            "presentation": 0.25,
            "materials": 0.25,
            "knowledge": 0.25,
            "communication": 0.25
        },
        "value_range": {"min": 1, "max": 10}
    }
    response1 = client.post('/calculate-rating', json=data)
    response2 = client.post('/calculate-rating', json=data)
    assert response1.json == response2.json
