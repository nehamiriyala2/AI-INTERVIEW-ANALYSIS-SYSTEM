import sounddevice as sd
import numpy as np

DURATION = 5        # seconds
SAMPLE_RATE = 44100

print("🎙️ Speak clearly for 5 seconds...")

# Record audio
audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype='float64'
)
sd.wait()

# Analyze volume (loudness)
volume = np.linalg.norm(audio)

print(f"Detected Voice Level: {volume:.2f}")

# Confidence logic
if volume < 15:
    result = "Voice Too Low ❌ (Not confident)"
elif volume < 35:
    result = "Voice Normal ⚠ (Can improve)"
else:
    result = "Voice Confident ✅ (Good)"

print("Analysis Result:", result)
