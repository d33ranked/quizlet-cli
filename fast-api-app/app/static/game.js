let currentWord = "";
let correctTranslation = "";
let score = 0;
let isAcceptingInput = false; 
let isWaitingForNextInput = false; // Renamed to handle both click and keyboard triggers

function toggleButtonState() {
    const inputField = document.getElementById("answer-input");
    const submitBtn = document.getElementById("submit-btn");
    
    if (!inputField || !submitBtn) return;

    if (isAcceptingInput && inputField.value.trim().length > 0) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
        submitBtn.style.cursor = "pointer";
    } else {
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.5";
        submitBtn.style.cursor = "not-allowed";
    }
}

async function nextWord() {
    const card = document.getElementById("word-card");
    const inputField = document.getElementById("answer-input");
    
    isAcceptingInput = false; 
    isWaitingForNextInput = false; // Reset the transition toggle
    toggleButtonState(); 

    card.classList.remove("state-correct", "state-incorrect");
    document.getElementById("start-btn").classList.add("hidden");
    if (inputField) inputField.value = "";
    
    try {
        const response = await fetch('/get-word');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Server error occurred.");
        }

        const data = await response.json();

        currentWord = data.word;
        correctTranslation = data.details.english_translation;
        
        document.getElementById("german-word").innerText = currentWord;
        document.getElementById("pos-tag").innerText = data.details.pos || "word";
        document.getElementById("example-sentence").innerText = data.details.example_sentence_native || "";
        
        document.getElementById("game-content").classList.remove("hidden");
        
        isAcceptingInput = true;
        toggleButtonState(); 
        
        setTimeout(() => inputField.focus(), 50);

    } catch (error) {
        document.getElementById("game-content").classList.add("hidden");
        document.getElementById("german-word").innerText = "⚠️ Error";
        document.getElementById("pos-tag").innerText = "";
        document.getElementById("example-sentence").innerText = error.message;
        card.classList.add("state-incorrect");
    }
}

function checkAnswer() {
    const inputField = document.getElementById("answer-input");
    if (!isAcceptingInput || !inputField || inputField.value.trim().length === 0) return;
    
    const userAnswer = inputField.value.trim().toLowerCase();
    const card = document.getElementById("word-card");

    isAcceptingInput = false; 
    toggleButtonState(); 

    if (userAnswer === correctTranslation.toLowerCase()) {
        score++;
        card.classList.add("state-correct");
    } else {
        card.classList.add("state-incorrect");
        inputField.value = `Correct: ${correctTranslation}`;
    }

    document.getElementById("score-val").innerText = score;
    
    // Set a tiny buffer delay before allowing a click/keypress to pull the next card.
    // This prevents the submission "Enter" keypress from being counted as the transition "Enter" keypress.
    setTimeout(() => {
        isWaitingForNextInput = true;
    }, 100);
}

document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("answer-input");
    
    if (inputField) {
        inputField.addEventListener("input", toggleButtonState);
    }
    
    // Central Keyboard Keydown Event Listener
    document.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            // Case A: The word is showing, input is valid, submit it
            if (isAcceptingInput && inputField && inputField.value.trim().length > 0) {
                checkAnswer();
            } 
            // Case B: The card is colored (waiting), hit Enter to advance
            else if (isWaitingForNextInput) {
                nextWord();
            }
        }
    });

    // Central Global Mouse Click Listener
    document.addEventListener("click", () => {
        if (isWaitingForNextInput) {
            nextWord();
        }
    });

    toggleButtonState();
});