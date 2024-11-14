const questionText = document.querySelector('.question-text');
const optionsContainer = document.querySelector('.options-section');
const feedback = document.getElementById('feedback');

// Fetch question and answers from the Flask backend
async function loadQuestion() {
    try {
        const response = await fetch('http://127.0.0.1:5000/get-question');
        let data = await response.json();

        // Parse if data is a string (debugging step we added)
        if (typeof data === "string") {
            data = JSON.parse(data);
        }

        // Populate question text
        questionText.innerHTML = data.question;

        // Prepare answer options with labels
        const options = [
            { text: data.answer_1, isCorrect: false },
            { text: data.answer_2, isCorrect: false },
            { text: data.answer_3, isCorrect: false },
            { text: data.true_answer_4_true, isCorrect: true } // True answer at the end
        ];

        // Shuffle the options array
        shuffleArray(options);

        // Clear previous options if any
        optionsContainer.innerHTML = '';

        // Add shuffled options as buttons
        options.forEach((option) => {
            const button = document.createElement('button');
            button.className = 'option';
            button.innerText = option.text;
            button.onclick = () => handleOptionClick(button, option.isCorrect);
            optionsContainer.appendChild(button);
        });
    } catch (error) {
        console.error("Error fetching question:", error);
    }
}

// Function to shuffle an array
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]]; // Swap elements
    }
}

// Handle option selection
function handleOptionClick(option, isCorrect) {
    // Disable all options after selection
    document.querySelectorAll('.option').forEach(btn => btn.disabled = true);

    if (isCorrect) {
        option.style.backgroundColor = '#d4edda';
        feedback.textContent = 'Correct! Well done.';
        feedback.classList.add('correct');
    } else {
        option.style.backgroundColor = '#f8d7da';
        feedback.textContent = 'Incorrect. Please review and try again.';
        feedback.classList.add('incorrect');
    }
}

// Load the question when the page loads
window.onload = loadQuestion;
