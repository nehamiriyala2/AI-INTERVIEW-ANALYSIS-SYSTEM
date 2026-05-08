/* ================= GLOBALS ================= */
let questions = [];
let qIndex = 0;

let recognition;
let finalTranscript = "";

let mediaRecorder;
let recordedChunks = [];

let isRunning = false;

/* ================= QUESTION BANK ================= */
const questionBank = {
    general: [
        "Tell me about yourself",
        "What are your strengths?",
        "What are your weaknesses?",
        "How do you handle pressure?",
        "Where do you see yourself in 5 years?"
    ],
    java: [
        "What is OOP in Java?",
        "Explain inheritance in Java",
        "What is JVM?"
    ],
    python: [
        "What are Python features?",
        "What is list comprehension?"
    ]
};

/* ================= START FLOW ================= */
function startInterviewFlow() {
    const tech = document.getElementById("techSelect").value;
    questions = questionBank[tech];
    qIndex = 0;
    loadQuestion();
}

/* ================= LOAD QUESTION ================= */
function loadQuestion() {

    finalTranscript = "";
    recordedChunks = [];

    document.getElementById("speechText").value = "";
    document.getElementById("emotionBadge").innerText = "Neutral 🙂";

    document.getElementById("questionText").innerText = questions[qIndex];
}

/* ================= START INTERVIEW ================= */
async function finishAnswer() {

    stopInterview();

    if (!finalTranscript.trim()) {
        alert("Please speak before finishing!");
        return;
    }

    const words = finalTranscript.trim().split(/\s+/).length;
    const score = Math.min(100, words * 2);

    const blob = new Blob(recordedChunks, { type: "video/webm" });

    const formData = new FormData();
    formData.append("video", blob);
    formData.append("answer", finalTranscript);
    formData.append("words", words);
    formData.append("score", score);
    formData.append("question", questions[qIndex]);
    formData.append("technology", document.getElementById("techSelect").value);

    try {

        const res = await fetch("/save_result", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            alert("Error saving interview result");
            return;
        }

        // 🔥 SHOW POPUP AFTER SUCCESSFUL SAVE
        const goNext = confirm(
            "Answer saved successfully ✅\n\nOK → Next Question\nCancel → View Result"
        );

        if (goNext) {

            qIndex++;

            if (qIndex < questions.length) {
                loadQuestion();
            } else {
                window.location.href = "/result";
            }

        } else {
            window.location.href = "/result";
        }

    } catch (error) {
        alert("Something went wrong!");
        console.error(error);
    }
}