from flask import Flask, request, render_template
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from io import BytesIO
from PIL import Image
import os
from keras.preprocessing import image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

model = tf.keras.models.load_model(
       ('model.h5'),
       custom_objects={'KerasLayer': hub.KerasLayer}
)
class_labels = ['boots', 'flip_flops', 'loafers', 'sandals', 'sneakers', 'soccer_shoes']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:
        img = Image.open(BytesIO(file.read()))
        img = img.resize((224, 224))
        img = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = img / 255.0
        result = model.predict(img)
        predicted_class = class_labels[np.argmax(result)]
        confidence = result[0][np.argmax(result)]*100
        confidence = round(confidence, 2)

        # Lấy danh sách các tệp ảnh trong thư mục của loại giày
        category_folder = os.path.join('static', 'uploads', predicted_class)
        if os.path.exists(category_folder):
            image_files = os.listdir(category_folder)
        else:
            image_files = []
        
        # Giới hạn số lượng ảnh hiển thị (ví dụ: 10 ảnh)
        image_files = image_files[:10]

        return render_template('result.html', predicted_class=predicted_class, confidence=confidence, image_files=image_files)

if __name__ == '__main__':
    app.run(debug=True)
