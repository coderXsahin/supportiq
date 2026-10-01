from fastapi import APIRouter
from pydantic import BaseModel

from app.ml.predictor import predict_category


router = APIRouter(
    prefix="/ml",
    tags=["Machine Learning"]
)


class PredictionRequest(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    text: str
    category: str


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    category = predict_category(request.text)

    return {
        "text": request.text,
        "category": category
    }