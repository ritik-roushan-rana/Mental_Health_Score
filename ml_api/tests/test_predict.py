from fastapi.testclient import TestClient
from app.main import app
from app.ml.loader import get_model

client = TestClient(app)

class FakeModel:
    def predict(self, X):
        return [6.5]

def override_get_model():
    return FakeModel()

app.dependency_overrides[get_model] = override_get_model

def test_predict_valid_input():
    response = client.post("/predict", json={
        "Age": 21,
        "Gender": "Male",
        "Academic_Level": "Undergraduate",
        "Most_Used_Platform": "Instagram",
        "Purpose_Of_Use": "Entertainment",
        "Avg_Daily_Usage_Hours": 4.5,
        "Study_Hours": 4.0,
        "Physical_Activity_Hours": 2.0,
        "Sleep_Hours_Per_Night": 6.5,
        "Stress_Level": "Medium",
        "Country_grouped_Canada": False,
        "Country_grouped_France": False,
        "Country_grouped_Germany": False,
        "Country_grouped_India": False,
        "Country_grouped_Mexico": False,
        "Country_grouped_Other": True,
        "Country_grouped_Turkey": False,
        "Country_grouped_UK": False,
        "Country_grouped_USA": False,
    })
    assert response.status_code == 200
    assert response.json()["predicted_mental_health_score"] == 6.5

def test_predict_rejects_invalid_category():
    response = client.post("/predict", json={
        "Age": 21,
        "Gender": "Male",
        "Academic_Level": "string",   # invalid — not in Literal options
        "Most_Used_Platform": "Instagram",
        "Purpose_Of_Use": "Entertainment",
        "Avg_Daily_Usage_Hours": 4.5,
        "Study_Hours": 4.0,
        "Physical_Activity_Hours": 2.0,
        "Sleep_Hours_Per_Night": 6.5,
        "Stress_Level": "Medium",
        "Country_grouped_Canada": False,
        "Country_grouped_France": False,
        "Country_grouped_Germany": False,
        "Country_grouped_India": False,
        "Country_grouped_Mexico": False,
        "Country_grouped_Other": True,
        "Country_grouped_Turkey": False,
        "Country_grouped_UK": False,
        "Country_grouped_USA": False,
    })
    assert response.status_code == 422