import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import os

MODEL_PATH = "models/current_model.mlmodel"  # Path to CoreML model

def load_model():
    """Load the current model from storage."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        # Optionally train a simple model for first-time setup
        model = LinearRegression()
        joblib.dump(model, MODEL_PATH)
        return model

def save_feedback(image, rating, user_rating, gender):
    """Save feedback data to the SQLite database."""
    conn = sqlite3.connect("feedback_storage.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            image BLOB,
            rating REAL,
            user_rating REAL,
            gender TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO feedback (image, rating, user_rating, gender)
        VALUES (?, ?, ?, ?)
    ''', (image, rating, user_rating, gender))
    conn.commit()
    conn.close()

def update_model():
    """Retrain and update the model with feedback data."""
    conn = sqlite3.connect("feedback_storage.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    feedback_data = cursor.fetchall()
    conn.close()

    if len(feedback_data) < 100:  # Define a threshold for retraining
        return False, "Not enough feedback data to update the model."

    # Extract features and labels
    images, ratings, user_ratings, genders = zip(*feedback_data)
    X = preprocess_images(images, genders)  # Pseudo-code for preprocessing
    y = user_ratings  # Use user ratings as target

    # Train model on new data
    model = LinearRegression()  # Simple linear model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model.fit(X_train, y_train)

    # Save the updated model
    joblib.dump(model, MODEL_PATH)
    return True, "Model successfully updated."


# --- Optional S3 integration for model storage ---

import boto3


def save_model_to_s3():
    s3 = boto3.client('s3')
    s3.upload_file(MODEL_PATH, 'your-s3-bucket-name', 'model/mlmodel')

def load_model_from_s3():
    s3 = boto3.client('s3')
    s3.download_file('your-s3-bucket-name', 'model/mlmodel', MODEL_PATH)
    return joblib.load(MODEL_PATH)

