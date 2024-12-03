// Get references to elements
const submitBtn = document.getElementById('submitBtn');
const feedback = document.getElementById('feedback');
const sentenceText = document.getElementById('sentenceText');

// Function to load fill-in-the-blank question from the backend
async function loadFillInTheBlank() {
    try {
        const response = await fetch('/get-fill-in-the-blank');
        const data = await response.json();

        console.log("Fetched data:", data);

        if (!data.fill_in_the_blank || !data.word) {
            console.error("Data is missing expected properties:", data);
            feedback.textContent = "Error loading question.";
            return;
        }

        const sentenceWithInput = data.fill_in_the_blank.replace("______", '<input type="text" id="userInput" placeholder="Type your answer here">');
        sentenceText.innerHTML = sentenceWithInput;

        const correctAnswer = data.word.toLowerCase();

        // Event listener for submit button to check answer and load next question
        submitBtn.onclick = async () => {
            const userInput = document.getElementById('userInput').value.trim().toLowerCase();
            document.getElementById('userInput').disabled = true;
            submitBtn.disabled = true;

            if (userInput === correctAnswer) {
                feedback.textContent = `Correct! "${correctAnswer.charAt(0).toUpperCase() + correctAnswer.slice(1)}" is the right answer.`;
                feedback.classList.add('correct');
            } else {
                feedback.textContent = `Incorrect. The correct answer is "${correctAnswer}".`;
                feedback.classList.add('incorrect');
            }

            // Load the next question after a short delay
            setTimeout(loadNextQuestion, 2000);
        };
    } catch (error) {
        console.error("Error fetching fill-in-the-blank question:", error);
        feedback.textContent = "Error loading question.";
    }
}

// Function to load the next question from the server
async function loadNextQuestion() {
    try {
        const response = await fetch('/next-question');
        const data = await response.json();

        // Check if there's a next question
        if (data.error) {
            sentenceText.innerHTML = "No more questions available.";
            feedback.innerHTML = "";
            submitBtn.disabled = true;
        } else if (data.fill_in_the_blank) {
            // If the next question is a fill-in-the-blank, reload it in the same format
            const sentenceWithInput = data.fill_in_the_blank.replace("______", '<input type="text" id="userInput" placeholder="Type your answer here">');
            sentenceText.innerHTML = sentenceWithInput;
            feedback.textContent = "";
            submitBtn.disabled = false;
            document.getElementById('userInput').disabled = false;

            // Store the new correct answer
            const correctAnswer = data.word.toLowerCase();

            // Re-attach event listener for new answer
            submitBtn.onclick = () => {
                const userInput = document.getElementById('userInput').value.trim().toLowerCase();
                document.getElementById('userInput').disabled = true;
                submitBtn.disabled = true;

                if (userInput === correctAnswer) {
                    feedback.textContent = `Correct! "${correctAnswer.charAt(0).toUpperCase() + correctAnswer.slice(1)}" is the right answer.`;
                    feedback.classList.add('correct');
                } else {
                    feedback.textContent = `Incorrect. The correct answer is "${correctAnswer}".`;
                    feedback.classList.add('incorrect');
                }

                // Load the next question after a short delay
                setTimeout(loadNextQuestion, 2000);
            };
        } else {
            sentenceText.innerHTML = "No more questions available.";
            feedback.innerHTML = "";
            submitBtn.disabled = true;
        }
    } catch (error) {
        console.error("Error fetching next question:", error);
        feedback.textContent = "Error loading the next question.";
    }
}

// Load the fill-in-the-blank question on page load
window.onload = loadFillInTheBlank;
