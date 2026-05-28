let currentWord = "";
let correctTranslation = "";
let score = 0;
let isAcceptingInput = false; // Starts as false until a word loads

// Helper function to manage button clickability safely
function toggleButtonState() {
    const inputField = document.getElementById("answer-input");
    const submitBtn = document.getElementById("submit-btn");
    
    if (!inputField || !submitBtn) return;

    // Button is ONLY clickable if we are accepting input AND the user typed something
    if (isAcceptingInput && inputField.value.trim().length > 0) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
        submitBtn.style.cursor = "pointer";
    } else {
        submitBtn.disabled = true;
        submitBtn.style.opacity = "0.5"; // Visual cue that it's unclickable
        submitBtn.style.cursor = "not-allowed";
    }
}

async function nextWord() {
    const card = document.getElementById("word-card");
    const inputField = document.getElementById("answer-input");
    
    isAcceptingInput = false;
    isWaitingForClick = false; // Reset the click blocker
    toggleButtonState(); // Instantly disable button while loading

    // Clear feedback state classes and reset inputs
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
        
        // Update content values
        document.getElementById("german-word").innerText = currentWord;
        document.getElementById("pos-tag").innerText = data.details.pos || "word";
        document.getElementById("example-sentence").innerText = data.details.example_sentence_native || "";
        
        // Reveal game content panels
        document.getElementById("game-content").classList.remove("hidden");
        
        // Now that the word is shown, allow input tracking
        isAcceptingInput = true;
        toggleButtonState(); // Will remain disabled until they type
        
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
    
    // Safety Guard: block execution if not accepting input or if input is empty
    if (!isAcceptingInput || !inputField || inputField.value.trim().length === 0) {
        return; 
    }
    
    const userAnswer = inputField.value.trim().toLowerCase();
    const card = document.getElementById("word-card");

    isAcceptingInput = false; 
    toggleButtonState(); // Locks the button out immediately so it can't be clicked again

    if (userAnswer === correctTranslation.toLowerCase()) {
        score++;
        card.classList.add("state-correct");
    } else {
        card.classList.add("state-incorrect");
        inputField.value = `Correct: ${correctTranslation}`;
    }

    document.getElementById("score-val").innerText = score;
    
    setTimeout(() => {
        isWaitingForClick = true;
    }, 50);
}



document.addEventListener("DOMContentLoaded", () => {
    const inputField = document.getElementById("answer-input");
    if (inputField) {
        // Listen for typing events to dynamically toggle the button state
        inputField.addEventListener("input", toggleButtonState);

        inputField.addEventListener("keypress", function(e) {
            // Only allow Enter key if the submit criteria is satisfied
            if (e.key === "Enter" && inputField.value.trim().length > 0) {
                checkAnswer();
            }
        });
    }
    
    // Global mouse left-click handler across the entire page
    document.addEventListener("click", (event) => {
        // If the game is paused waiting for a click, advance to the next word
        if (isWaitingForClick) {
            nextWord();
        }
    });

    toggleButtonState();
});