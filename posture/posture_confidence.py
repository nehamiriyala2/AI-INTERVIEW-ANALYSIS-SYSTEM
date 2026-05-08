import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    posture = "Not Detected"

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                    lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        ear = [lm[mp_pose.PoseLandmark.LEFT_EAR].x,
               lm[mp_pose.PoseLandmark.LEFT_EAR].y]
        hip = [lm[mp_pose.PoseLandmark.LEFT_HIP].x,
               lm[mp_pose.PoseLandmark.LEFT_HIP].y]

        angle = calculate_angle(ear, shoulder, hip)

        if angle > 160:
            posture = "Good Posture ✅"
            color = (0, 255, 0)
        else:
            posture = "Poor Posture ⚠"
            color = (0, 0, 255)

        cv2.putText(
            image,
            f"Posture: {posture}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        mp_draw.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.imshow("Posture Confidence - AI Interview", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
