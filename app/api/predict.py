from fastapi import APIRouter, Depends
import pandas as pd
from app.models.schemas import MentalHealthInput, PredictionOutput
from app.ml.loader import get_model

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
def predict(input_data: MentalHealthInput, model=Depends(get_model)):
    input_df = pd.DataFrame([input_data.model_dump()])
    prediction = model.predict(input_df)[0]
    return PredictionOutput(predicted_mental_health_score=round(float(prediction), 2))