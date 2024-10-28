from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import sqlite3
from model_utils import load_model, update_model, save_feedback

app = Flask(__name__)
api = Api(app)

# Homepage
@app.route('/')

def home():
    return render_template('index.html')

# Initialize the model at the start
model = load_model()

class Predict(Resource):
    def post(self):
        data = request.json
        image = data.get("image")
        gender = data.get("gender")

        # Run prediction (pseudo-code, assuming a preprocess function exists)
        rating = model.predict(preprocess(image, gender))
        
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