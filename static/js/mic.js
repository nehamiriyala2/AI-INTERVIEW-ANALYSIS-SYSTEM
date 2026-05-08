

let recognition;
let finalText = "";
let isListening = false;

window.onload = () => {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            let transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalText += transcript + " ";
            } else {
                interim += transcript;
            }
        }

        document.getElementById("answerText").innerText =
            finalText + interim;
    };

    recognition.onerror = (e) => {
        console.error("Speech error:", e);
    };
};

function startSpeaking() {
    if (!isListening) {
        finalText = "";
        recognition.start();
        isListening = true;
        document.getElementById("micStatus").innerText = "🎤 Listening...";
    }
}

function stopAndAnalyze() {
    if (isListening) {
        recognition.stop();
        isListening = false;
        document.getElementById("micStatus").innerText = "⏳ Analyzing...";

        fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: finalText
            })
        })
        .then(res => res.json())
        .then(data => {
            window.location.href = "/result";
        })
        .catch(err => {
            alert("Analyze failed");
            console.error(err);
        });
    }
}