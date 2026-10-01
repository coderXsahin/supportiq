import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


DATASET_PATH = "app/ml/dataset.csv"
MODEL_PATH = "app/ml/ticket_classifier.pkl"


# Load dataset
df = pd.read_csv(DATASET_PATH)

X = df["text"]
y = df["category"]


# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Build ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2)
    )),
    ("classifier", LogisticRegression(
        max_iter=1000
    ))
])


# Train model
model.fit(X_train, y_train)


# Evaluate on unseen test data
predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)


print("Model Training & Evaluation")
print("===========================")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")
print(f"Accuracy: {accuracy:.4f}")
print()
print("Classification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)


# Save trained model
joblib.dump(
    model,
    MODEL_PATH
)

print()
print(f"Model saved to: {MODEL_PATH}")