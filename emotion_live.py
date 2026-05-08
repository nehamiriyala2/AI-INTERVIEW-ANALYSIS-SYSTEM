import cv2
import numpy as np
import requests
from tensorflow.keras.models import load_model

# ---------------- CONFIG ----------------
FLASK_URL = "http://127.0.0.1:5000/update_emotion"

EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# ---------------- LOAD MODEL ----------------
model = load_model("models/emotion_model.h5", compile=False)
face_cascade = cv2.CascadeClassifier(
    "backend/haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)
last_emotion = "Neutral"

print("🎥 Emotion detection started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    emotion_detected = "Neutral"

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (64, 64))
        face = face / 255.0
        face = face.reshape(1, 64, 64, 1)

        preds = model.predict(face, verbose=0)
        emotion_detected = EMOTIONS[np.argmax(preds)]

        # draw box
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(
            frame,
            emotion_detected,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0,255,0),
            2
        )

    # 🔥 SEND TO FLASK ONLY IF CHANGED
    if emotion_detected != last_emotion:
        try:
            requests.post(
                FLASK_URL,
                json={"emotion": emotion_detected},
                timeout=1
            )
            print("➡ Emotion sent:", emotion_detected)
            last_emotion = emotion_detected
        except:
            print("⚠ Flask not reachable")

    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()