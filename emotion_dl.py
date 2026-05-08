import cv2
import numpy as np
from tensorflow.keras.models import load_model

# load model
emotion_model = load_model("models/emotion_model.h5")

emotion_labels = [
    "Angry", "Disgust", "Fear",
    "Happy", "Sad", "Surprise", "Neutral"
]

face_cascade = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)

def detect_emotion(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return "Neutral"

    (x, y, w, h) = faces[0]
    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, (48, 48))
    face = face / 255.0
    face = face.reshape(1, 48, 48, 1)

    prediction = emotion_model.predict(face, verbose=0)
    emotion = emotion_labels[np.argmax(prediction)]

    return emotion