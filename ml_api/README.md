# Mental Health Score Predictor

A FastAPI service that estimates a student's mental health score (0–10) from their digital habits, study routine, sleep, activity level, and stress — powered by a tuned Random Forest model trained on student lifestyle survey data.

## What this is

- A trained ML pipeline (preprocessing + Random Forest Regressor) wrapped in a FastAPI backend
- A `/predict` endpoint with strict Pydantic validation
- A plain HTML/CSS/JS frontend served from the same app (no CORS needed)
- A `/health` endpoint for uptime checks

## Model performance

| Model | R² | RMSE | MAE |
|---|---|---|---|
| Linear Regression | 0.7436 | 0.6765 | 0.5330 |
| Random Forest (untuned) | 0.8729 | 0.4763 | 0.3517 |
| **Random Forest (tuned)** | **0.9058** | **0.4101** | **0.2888** |

The final model explains ~91% of the variance in mental health score, with a typical prediction error under 0.3 points on a scale of roughly 3.6–9.4.

## Project structure

```
ml_api/
├── app/
│   ├── main.py              # app setup, lifespan model loading, route registration
│   ├── api/
│   │   └── predict.py       # POST /predict route
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response schemas
│   └── ml/
│       └── loader.py        # shared model dict + get_model dependency
├── static/
│   ├── index.html           # form UI
│   ├── style.css
│   └── script.js            # fetch() calls to /predict, gauge rendering
├── tests/
│   └── test_predict.py      # TestClient tests with a mocked model
├── model_artifacts/
│   └── mental_health_pipeline.joblib   # trained sklearn pipeline
├── .env                     # local config (not committed)
├── requirements.txt
└── Dockerfile                # placeholder, not yet built out
```

## Setup

```bash
# from the project root
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
MODEL_PATH=model_artifacts/mental_health_pipeline.joblib
```

## Running locally

```bash
cd ml_api
fastapi dev app/main.py
```

Then open:
- `http://127.0.0.1:8000/` — the prediction form
- `http://127.0.0.1:8000/docs` — interactive API docs (Swagger UI)
- `http://127.0.0.1:8000/health` — health check

## Running tests

```bash
cd ml_api
pytest tests/
```

Tests use `app.dependency_overrides` to swap in a fake model, so they run without needing the real `.joblib` file or making real predictions.

## API

### `POST /predict`

Request body (all fields required unless noted):

```json
{
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
  "Country_grouped_Canada": false,
  "Country_grouped_France": false,
  "Country_grouped_Germany": false,
  "Country_grouped_India": false,
  "Country_grouped_Mexico": false,
  "Country_grouped_Other": true,
  "Country_grouped_Turkey": false,
  "Country_grouped_UK": false,
  "Country_grouped_USA": false
}
```

Valid categorical values:
- `Gender`: `Male`, `Female`
- `Academic_Level`: `High School`, `Undergraduate`, `Graduate`
- `Stress_Level`: `Low`, `Medium`, `High`, `Very High`
- `Most_Used_Platform`: `Facebook`, `LinkedIn`, `Instagram`, `Snapchat`, `Twitter`, `YouTube`, `TikTok`, `LINE`, `KakaoTalk`, `VKontakte`, `WhatsApp`, `WeChat`
- `Purpose_Of_Use`: `Networking`, `Education`, `Entertainment`, `News`

Invalid values (e.g. a typo, or an out-of-range number) are rejected with a `422` before reaching the model.

Response:

```json
{
  "predicted_mental_health_score": 6.8
}
```

### `GET /health`

```json
{
  "status": "ok",
  "model_loaded": true
}
```

## How the model was built

1. Cleaned invalid values (e.g. negative `Physical_Activity_Hours`, clipped to 0)
2. Checked skewness — all features were fairly symmetric, no transforms needed
3. Grouped low-frequency countries into `Other`, one-hot encoded the rest
4. Ordinal-encoded `Academic_Level` and `Stress_Level` (order-preserving)
5. One-hot encoded remaining nominal categoricals (`Gender`, `Most_Used_Platform`, `Purpose_Of_Use`)
6. Compared Linear Regression, Random Forest, and tuned Random Forest (`RandomizedSearchCV`, 5-fold CV)
7. Selected tuned Random Forest as the final model based on test-set R²/RMSE/MAE
8. Saved the full preprocessing + model pipeline as a single `.joblib` file, so raw input in → prediction out, with no separate preprocessing step to manage at inference time

## Notes

- This is a statistical estimate for reflection, not a clinical or diagnostic tool.
- The dataset's unusually clean correlations suggest it may be synthetic rather than collected survey data — worth keeping in mind before drawing real-world conclusions from it.