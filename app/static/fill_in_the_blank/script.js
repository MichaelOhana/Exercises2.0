// References to DOM elements
const submitBtn = document.getElementById('submitBtn');
const feedback = document.getElementById('feedback');
const sentenceText = document.getElementById('sentenceText');

// Function to load the fill-in-the-blank question
async function loadFillInTheBlank() {
    try {
        const response = await fetch('/get-fill-in-the-blank');
        const data = await response.json();

        if (!data.fill_in_the_blank || !data.word) {
            feedback.textContent = "Error loading question.";
            return;
        }

        // Access the sentence from the nested object
        const sentenceTemplate = data.fill_in_the_blank.sentence;

        // Replace '{{blank}}' with an input field
        const sentenceWithInput = sentenceTemplate.replace('{{blank}}', '<input type="text" id="userInput" placeholder="Your answer here">');
        sentenceText.innerHTML = sentenceWithInput;

        // Correct answer
        const correctAnswer = data.word.toLowerCase();

        // Event listener for the submit button
        submitBtn.onclick = () => {
            const userInput = document.getElementById('userInput').value.trim().toLowerCase();
            document.getElementById('userInput').disabled = true;
            submitBtn.disabled = true;

            if (userInput === correctAnswer) {
                feedback.textContent = `Correct! "${data.word}" is the right answer.`;
                feedback.classList.add('correct');
            } else {
                feedback.textContent = `Incorrect. The correct answer is "${data.word}".`;
                feedback.classList.add('incorrect');
            }

            // Load the next question after a delay
            setTimeout(() => {
                window.location.href = '/questions';
            }, 3000);
        };
    } catch (error) {
        console.error("Error fetching fill-in-the-blank question:", error);
        feedback.textContent = "Error loading question.";
    }
}

// Load the question on page load
window.onload = loadFillInTheBlank;
