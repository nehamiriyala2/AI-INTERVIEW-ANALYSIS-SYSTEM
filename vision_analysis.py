import cv2

def analyze_video(video_path):
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        cap = cv2.VideoCapture(video_path)

        total_frames = 0
        face_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                face_frames += 1

        cap.release()

        if total_frames == 0:
            return 0, "Neutral"

        score = face_frames / total_frames

        # Since we are not doing emotion detection yet
        detected_emotion = "Neutral"

        return score, detected_emotion

    except Exception as e:
        print("Vision Error:", e)
        return 0, "Neutral"