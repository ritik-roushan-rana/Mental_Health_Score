from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import joblib
from dotenv import load_dotenv
import os

from app.ml.loader import ml_models
from app.api.predict import router as predict_router

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "model_artifacts/mental_health_pipeline.joblib")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["pipeline"] = joblib.load(MODEL_PATH)
    print("Model loaded successfully")
    yield
    ml_models.clear()
    print("Model cleared from memory")

app = FastAPI(lifespan=lifespan)
app.include_router(predict_router)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "pipeline" in ml_models}

app.mount("/", StaticFiles(directory="static", html=True), name="static")