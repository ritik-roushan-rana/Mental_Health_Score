# Mental Health Score Predictor

**Live demo:** [mental-health-score-0ues.onrender.com](https://mental-health-score-0ues.onrender.com/) (free tier — first request after idling takes ~30-60s to cold-start)

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
| **Random Forest (tuned, depth-capped)** | **0.9030** | **0.4101** | **0.3018** |

The final model explains ~90% of the variance in mental health score, with a typical prediction error under 0.3 points on a scale of roughly 3.6–9.4. Tree depth is capped (`max_depth=18`) so the serialized pipeline stays small (~10MB) and loads in well under 512MB of RAM — the original unbounded trees scored marginally higher (R² 0.9058) but needed ~555MB just to unpickle, which OOM'd on free-tier hosting.

## Project structure

```
.
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
│   └── mental_health_pipeline.joblib   # trained sklearn pipeline (compressed)
├── .env                     # local config (not committed)
├── requirements.txt
├── Dockerfile               # container build for deployment
├── render.yaml              # Render blueprint (Docker web service)
└── .dockerignore
```

## Setup

```bash
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
fastapi dev app/main.py
```

Then open:
- `http://127.0.0.1:8000/` — the prediction form
- `http://127.0.0.1:8000/docs` — interactive API docs (Swagger UI)
- `http://127.0.0.1:8000/health` — health check

## Running tests

```bash
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

## Deployment

The app is containerized with the included `Dockerfile`, which installs `requirements.txt`, copies `app/`, `static/`, and `model_artifacts/`, and serves via `uvicorn`. It reads the `PORT` env var if set (falling back to `7860`), so the same image works on both platforms below.

### Render

Live at **[mental-health-score-0ues.onrender.com](https://mental-health-score-0ues.onrender.com/)**.

1. Push this repo to GitHub (already done if you're reading this from the repo).
2. In the [Render dashboard](https://dashboard.render.com/), click **New > Blueprint** and connect this GitHub repo. Render will detect `render.yaml` and configure a Docker web service (`mental-health-score`) automatically, including the `/health` health check path.
   - No `render.yaml`? Use **New > Web Service** instead, connect the repo, set **Runtime** to `Docker`, and leave the build/start commands as defined by the `Dockerfile`.
3. Render assigns a public URL (e.g. `https://<service-name>.onrender.com`) — click **Deploy** and it builds the Dockerfile and starts the app, binding to the `PORT` Render provides.
4. To update after future code changes: `git push origin main` — Render auto-deploys on push (if auto-deploy is enabled on the service).

Note: the free plan spins the service down after inactivity, so the first request after idling takes ~30-60s to cold-start. It's also capped at 512MB RAM, which is why the model uses depth-capped trees (see [Model performance](#model-performance)).

### Hugging Face Spaces

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space):
   - **SDK**: Docker
   - **Hardware**: CPU basic (free tier is enough for this model)
2. Give the Space its own git remote and push this repo to it:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space main
   ```
   (Authenticate with a Hugging Face access token when prompted for a password — generate one at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).)
3. The Space builds the `Dockerfile` automatically and starts the app. Once the build finishes, it's live at:
   ```
   https://<your-username>-<space-name>.hf.space
   ```
4. To update after future code changes: commit, then `git push origin main` (GitHub) and `git push space main` (Hugging Face) — the Space rebuilds automatically on push.

### Running the container locally (optional sanity check before deploying)

```bash
docker build -t mental-health-score .
docker run -p 7860:7860 mental-health-score
```

Then visit `http://localhost:7860/`.