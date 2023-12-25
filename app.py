from flask import Flask, request, render_template, jsonify
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from io import BytesIO
from PIL import Image
import os
from keras.preprocessing import image
import mysql.connector
from flask_cors import CORS  # Import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = 'uploads'

# Kết nối đến cơ sở dữ liệu MySQL trong XAMPP
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pbl6"
)

cursor = db.cursor()

model = tf.keras.models.load_model(
       'model.h5',
       custom_objects={'KerasLayer': hub.KerasLayer}
)

class_labels = ['boots', 'flip_flops', 'loafers', 'sandals', 'sneakers', 'soccer_shoes']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        img = Image.open(BytesIO(file.read()))
        img = img.resize((224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = img / 255.0
        result = model.predict(img)
        predicted_class = class_labels[np.argmax(result)]
        confidence = result[0][np.argmax(result)] * 100
        confidence = round(confidence, 2)
        
        if predicted_class == 'flip_flops':
            predicted_class = 'Flip-flop'
        elif predicted_class == 'sneakers':
            predicted_class = 'Sneaker'
        elif predicted_class == 'loafers':
            predicted_class = 'Loafer'
        elif predicted_class == 'boots':
            predicted_class = 'Boot'
        elif predicted_class == 'sandals':
            predicted_class = 'Sandal'
        else:
            predicted_class = 'Soccer shoe'

        # Truy vấn cơ sở dữ liệu để lấy thông tin giày từ DB
        query = (
            "SELECT s.id, s.name AS shoe_name, s.price, i.image AS shoe_image, c.name AS category_name, c.image AS category_image FROM shoes s JOIN categories c ON s.id_category = c.id JOIN images i ON s.id = i.id_shoes WHERE c.name = '{predicted_class}';")
        # query = (
        #     "SELECT s.id, s.name AS shoe_name, s.price, i.image AS shoe_image, c.name AS category_name, c.image AS category_image "
        #     "FROM shoes s "
        #     "JOIN categories c ON s.id_category = c.id "
        #     "JOIN images i ON s.id = i.id_shoes "
        #     "WHERE c.name = '{predicted_class}';"
        # )
        cursor.execute(query.format(predicted_class=predicted_class))
        shoe_info = cursor.fetchall()

        shoe_list = []
        for row in shoe_info:
            shoe_id, shoe_name, price, shoe_image, category_name, category_image = row
            shoe_list.append({
                'shoe_id': shoe_id,
                'shoe_name': shoe_name,
                'price': price,
                'shoe_image': shoe_image,
                'category_name': category_name,
                'category_image': category_image
            })

        # Return the shoe_list in JSON format
        return jsonify({
            "predicted_class": predicted_class,
            "confidence": confidence,
            "shoe_list": shoe_list,
        })


if __name__ == '__main__':
    app.run(debug=True)
    
