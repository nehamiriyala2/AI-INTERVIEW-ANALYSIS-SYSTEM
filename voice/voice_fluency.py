import sounddevice as sd
import numpy as np

DURATION = 6
SAMPLE_RATE = 44100

print("🎙️ Speak naturally for 6 seconds...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='float64'
)
sd.wait()

audio = audio.flatten()

# 1️⃣ Volume (confidence)
volume = np.linalg.norm(audio)

# 2️⃣ Clarity (signal smoothness)
clarity = np.std(audio)

# 3️⃣ Fluency (speech activity)
speech_frames = np.sum(np.abs(audio) > 0.02)

# ----- Analysis -----
score = 0

# Volume score
if volume > 40:
    volume_result = "Good"
    score += 2
elif volume > 20:
    volume_result = "Normal"
    score += 1
else:
    volume_result = "Low"

# Clarity score
if clarity < 0.04:
    clarity_result = "Clear"
    score += 2
elif clarity < 0.07:
    clarity_result = "Fair"
    score += 1
else:
    clarity_result = "Poor"

# Fluency score
if speech_frames > 80000:
    fluency_result = "Fast"
    score += 1
elif speech_frames > 50000:
    fluency_result = "Normal"
    score += 2
else:
    fluency_result = "Slow"

# Final Rating
if score >= 5:
    rating = "⭐⭐⭐⭐⭐ Excellent"
elif score >= 4:
    rating = "⭐⭐⭐⭐ Good"
elif score >= 3:
    rating = "⭐⭐⭐ Average"
else:
    rating = "⭐ Needs Improvement"

print("\n--- INTERVIEW VOICE ANALYSIS ---")
print("Volume (Confidence):", volume_result)
print("Clarity:", clarity_result)
print("Fluency:", fluency_result)
print("Final Rating:", rating)
