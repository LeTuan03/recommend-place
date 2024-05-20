from flask import Flask,  request, jsonify
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection settings
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'traveldb'
}


# Function to load data from the database
def load_data_from_db():
    connection = pymysql.connect(**db_config)
    try:
        user_data_query = "SELECT * FROM user_data"
        location_data_query = "SELECT * FROM location_data"
        ratings_query = "SELECT * FROM ratings"

        user_data = pd.read_sql(user_data_query, connection)
        location_data = pd.read_sql(location_data_query, connection)
        ratings = pd.read_sql(ratings_query, connection)
    finally:
        connection.close()

    return user_data, location_data, ratings


# Load data from the database
user_data, location_data, ratings = load_data_from_db()

# Encoding location data
location_encoder = LabelEncoder()
location_data["location_index"] = location_encoder.fit_transform(location_data["location_id"])
ratings["location_index"] = location_encoder.transform(ratings["location_id"])

# Create train and test datasets
train = tf.data.Dataset.from_tensor_slices((
    {"user_id": ratings["user_id"], "location_id": ratings["location_index"]},
    ratings["rating"]
)).shuffle(len(ratings))

test = tf.data.Dataset.from_tensor_slices((
    {"user_id": ratings["user_id"], "location_id": ratings["location_index"]},
    ratings["rating"]
)).batch(len(location_data))

# Model architecture
user_id = tf.keras.Input(shape=(), name="user_id", dtype=tf.int32)
location_id = tf.keras.Input(shape=(), name="location_id", dtype=tf.int32)
user_embedding = tf.keras.layers.Embedding(input_dim=len(user_data), output_dim=32)(user_id)
location_embedding = tf.keras.layers.Embedding(input_dim=len(location_data), output_dim=32)(location_id)
dot_product = tf.keras.layers.Dot(axes=1)([user_embedding, location_embedding])
model = tf.keras.Model(inputs=[user_id, location_id], outputs=dot_product)

model.compile(optimizer=tf.keras.optimizers.Adagrad(0.1), loss=tf.keras.losses.MeanSquaredError(), metrics=["accuracy"])

model.evaluate(test)


# Function to recommend locations for a specific user ID
def recommend_locations_for_user(user_id, model, location_encoder, location_data, num_recommendations=10):
    locations_for_specific_user = tf.data.Dataset.from_tensor_slices({
        "user_id": np.repeat(user_id, len(location_data)),
        "location_id": np.arange(len(location_data))  # Use location_index instead of location_name
    })

    # Reshape the input tensors to match the expected shapes
    locations_for_specific_user = locations_for_specific_user.map(lambda x: {
        "user_id": tf.reshape(x["user_id"], (1,)),
        "location_id": tf.reshape(x["location_id"], (1,))
    })

    # Predict ratings for locations for the specific userId
    predicted_ratings = model.predict(locations_for_specific_user)

    # Combine location_index with predicted ratings
    predicted_ratings_with_indexes = list(zip(np.arange(len(location_data)), predicted_ratings))

    # Sort by predicted ratings
    recommended_locations_indexes = sorted(predicted_ratings_with_indexes, key=lambda x: x[1], reverse=True)

    # Choose the desired number of recommended locations
    top_recommendations_indexes = recommended_locations_indexes[:num_recommendations]

    # Decode location indexes back to location names
    top_recommendations = [(location_encoder.inverse_transform([index])[0], rating) for index, rating in
                           top_recommendations_indexes]

    return top_recommendations


@app.route('/recommend_locations')
def recommend_locations():
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return jsonify({"message": "Please provide a valid user_id parameter."}), 400

    recommendations = recommend_locations_for_user(user_id, model, location_encoder, location_data)

    # Chuyển đổi các giá trị `location_id` và `rating` thành kiểu dữ liệu cơ bản của Python
    list_recommend = [str(location) for location, rating in recommendations]

    return jsonify({"data": list_recommend}), 200

def get_location_details(location_id):
    connection = pymysql.connect(**db_config)
    try:
        query = "SELECT * FROM location_data WHERE location_id = %s"
        location_data = pd.read_sql(query, connection, params=[location_id])
        return location_data.to_dict(orient='records')
    finally:
        connection.close()

@app.route('/location_details')
def location_details():
    location_id = request.args.get('location_id', type=int)
    if location_id is None:
        return jsonify({"message": "Please provide a valid location_id parameter."}), 400

    details = get_location_details(location_id)
    if not details:
        return jsonify({"message": "Location not found."}), 404

    return jsonify(details), 200


@app.route('/login', methods=['POST'])
def login():
    user_name = request.json.get('user_name')
    password = request.json.get('password')

    if not user_name or not password:
        return jsonify({"message": "Please provide both username and password"}), 400

    connection = pymysql.connect(**db_config)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data WHERE user_name = %s AND password = %s", (user_name, password))
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "Login successful", "user_id": user[0]}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
