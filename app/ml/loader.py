from fastapi import HTTPException

ml_models = {}

def get_model():
    if "pipeline" not in ml_models:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return ml_models["pipeline"]