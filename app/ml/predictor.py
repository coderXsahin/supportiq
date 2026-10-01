import joblib


MODEL_PATH = "app/ml/ticket_classifier.pkl"

model = joblib.load(MODEL_PATH)


def predict_category(text: str) -> str:
    prediction = model.predict([text])

    return prediction[0]