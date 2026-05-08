import cv2
import numpy as np
from tensorflow.keras.models import load_model
import requests

MODEL_PATH = "models/emotion_model.h5"
CASCADE_PATH = "backend/haarcascade_frontalface_default.xml"

model = load_model(MODEL_PATH, compile=False)
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

def start_emotion_detection():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion = "Neutral"

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (64, 64))
            face = face / 255.0
            face = face.reshape(1, 64, 64, 1)

            preds = model.predict(face, verbose=0)
            emotion = EMOTIONS[np.argmax(preds)]

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,255), 2)
            cv2.putText(frame, emotion, (x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 2)

        # 🔥 SEND LIVE EMOTION TO FLASK
        try:
            requests.post(
                "http://127.0.0.1:5000/update_emotion",
                json={"emotion": emotion},
                timeout=0.1
            )
        except:
            pass

        cv2.imshow("AI Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()