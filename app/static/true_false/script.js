const statementText = document.getElementById('statementText');
const feedback = document.getElementById('feedback');
const trueBtn = document.getElementById('trueBtn');
const falseBtn = document.getElementById('falseBtn');

// Load true/false question
async function loadTrueFalse() {
    try {
        const response = await fetch('/get-true-false');
        const data = await response.json();

        if (!data.true_false || !data.true_false.statement || typeof data.true_false.is_true !== 'boolean') {
            feedback.textContent = "Error loading question.";
            return;
        }

        // Display the statement
        statementText.textContent = data.true_false.statement;

        // Correct answer
        const isTrue = data.true_false.is_true;

        // Event listeners for True and False buttons
        trueBtn.onclick = () => handleAnswer(true);
        falseBtn.onclick = () => handleAnswer(false);

        function handleAnswer(userChoice) {
            // Disable buttons after selection
            trueBtn.disabled = true;
            falseBtn.disabled = true;

            if (userChoice === isTrue) {
                feedback.textContent = 'Correct!';
                feedback.classList.add('correct');
            } else {
                feedback.textContent = 'Incorrect.';
                feedback.classList.add('incorrect');
            }

            // Load the next question after a delay
            setTimeout(() => {
                window.location.href = '/questions';
            }, 3000);
        }
    } catch (error) {
        console.error("Error fetching true/false question:", error);
        feedback.textContent = "Error loading question.";
    }
}

// Load the question on page load
window.onload = loadTrueFalse;
