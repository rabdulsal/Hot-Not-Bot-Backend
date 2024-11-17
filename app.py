from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
# import sqlite3
import requests
import os
from model_utils import load_model, preprocess_images, update_model, save_feedback

app = Flask(__name__)
api = Api(app)

# Keep track of the number of model updates
update_count = 0
UPDATE_THRESHOLD = 1000  # Trigger push notification after this many updates

# Routing
@app.route('/')
@app.route('/update-model', methods=['POST'])


def update_model():
    global update_count
    # Simulate model update logic (e.g., receiving and processing new ratings)
    update_count += 1

    if update_count >= UPDATE_THRESHOLD:
        send_push_notification()
        update_count = 0  # Reset the count after sending notification

    return {"status": "Model updated successfully."}

# Function to send push notifications via Firebase
def send_push_notification():
    FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")  # Add your Firebase server key here
    FCM_URL = "https://fcm.googleapis.com/fcm/send"
    message = {
        "to": "/topics/model_updates",  # All devices subscribed to this topic
        "notification": {
            "title": "New Model Update!",
            "body": "A new model version is ready. Update now for the latest improvements!"
        },
        "data": {
            "type": "model_update"
        }
    }
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(FCM_URL, json=message, headers=headers)
    print(f"Push notification sent: {response.status_code}, {response.text}")

# Homepage
def home():
    return render_template('index.html', static_folder='./static')

# Initialize the model at the start
model = load_model()

class Predict(Resource):

    def post(self):
        data = request.json
        image = data.get("image")
        gender = data.get("gender")

        # Run prediction (pseudo-code, assuming a preprocess function exists)
        rating = model.predict(preprocess_images(image, gender))
        return jsonify({"rating": rating})


class Feedback(Resource):
    def post(self):
        data = request.json
        image = data.get("image")
        rating = data.get("rating")
        user_rating = data.get("user_rating")
        gender = data.get("gender")

        # Save feedback data to SQLite
        save_feedback(image, rating, user_rating, gender)

        return jsonify({"status": "success", "message": "Feedback received"})


class UpdateModel(Resource):
    def post(self):
        # Trigger model retraining
        success, message = update_model()

        if success:
            return jsonify({"status": "success", "message": "Model updated"})
        else:
            return jsonify({"status": "error", "message": message})


api.add_resource(Predict, '/predict')
api.add_resource(Feedback, '/feedback')
api.add_resource(UpdateModel, '/update-model')

if __name__ == '__main__':
    app.run(debug=True)
