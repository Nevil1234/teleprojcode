from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import requests  # Add this import for sending images to Telegram

app = Flask(__name__)
CORS(app)

TOKEN = "7094792264:AAEH-QrZhteAOaFoHoCZEk54iyzhud1Tck4"  # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "5949257717"  # Replace with your Telegram chat ID
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

MODEL = tf.keras.models.load_model("D:\\code of hackathon\\codes\\2")

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data))
    image = image.resize((256, 256))
    image = np.array(image)
    return image

def capture_and_predict():
    camera_port = 'D:\code of hackathon\telecode\stock-footage-early-blight-disease-on-potato-crops-damaged-green-and-yellow-leaves-with-brown-spots-caused-by.webm'
    camera = cv2.VideoCapture(camera_port)
    
    while True:
        ret, frame = camera.read()
        imgencode = cv2.imencode('.jpg', frame)[1]
        image_data = imgencode.tostring()

        # Send the image to Telegram bot
        files = {'photo': ('image.jpg', image_data)}
        payload = {'chat_id': TELEGRAM_CHAT_ID}
        requests.post(TELEGRAM_API_URL, files=files, data=payload)

        # Perform prediction on the captured image
        image = read_file_as_image(image_data)
        img_batch = np.expand_dims(image, 0)
        predictions = MODEL.predict(img_batch)

        predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
        confidence = float(np.max(predictions[0]))

        # Send the prediction results to Telegram bot
        message = f"Prediction: {predicted_class}\nConfidence: {confidence}"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        requests.post("https://api.telegram.org/bot{}/sendMessage".format(TOKEN), data=payload)

        # Yield the frame for video feed
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image_data + b'\r\n')

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(capture_and_predict(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
