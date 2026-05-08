def generate_report(emotion, voice, posture):
    e = 30 if emotion == "Happy" else 20
    v = 32 if "⭐⭐⭐⭐" in voice else 24
    p = 30 if posture == "Good" else 15

    total = e + v + p

    status = "Interview Ready ✅" if total >= 80 else "Needs Improvement ⚠"

    return {
        "emotion": emotion,
        "voice": voice,
        "posture": posture,
        "score": total,
        "status": status
    }
