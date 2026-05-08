import cv2
from deepface import DeepFace

def detect_emotion():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Neutral"

    try:
        result = DeepFace.analyze(
            frame,
            actions=["emotion"],
            enforce_detection=False
        )
        return result[0]["dominant_emotion"].capitalize()
    except:
        return "Neutral"
