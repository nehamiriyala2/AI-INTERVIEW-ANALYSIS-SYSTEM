# analysis_data = {
#     "emotion": "Neutral",
#     "voice": "⭐⭐⭐ Average",
#     "posture": "Pending",
#     "score": 0,
#     "status": "Not Evaluated"
# }

# This file stores all interview records

# interviews = []

# def add_interview(score, emotion, voice, fluency, structure):
#     interviews.append({
#         "score": score,
#         "emotion": emotion,
#         "voice": voice,
#         "fluency": fluency,
#         "structure": structure
#     })

# def get_all_interviews():
#     return interviews



# backend/data_store.py

interviews = []

def add_interview(data):
    interviews.append(data)

def get_all_interviews():
    return interviews

def get_summary():
    total = len(interviews)

    if total == 0:
        return {
            "total": 0,
            "last_score": 0,
            "avg_score": 0
        }

    last_score = interviews[-1]["score"]
    avg_score = round(sum(i["score"] for i in interviews) / total, 2)

    return {
        "total": total,
        "last_score": last_score,
        "avg_score": avg_score
    }