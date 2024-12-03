const questionText = document.getElementById('questionText');
const optionsContainer = document.getElementById('optionsContainer');
const feedback = document.getElementById('feedback');

// Load multiple-choice question
async function loadMultipleChoice() {
    try {
        const response = await fetch('/get-multiple-choice');
        const data = await response.json();

        if (!data.multiple_choice || !data.multiple_choice.question || !data.multiple_choice.options) {
            feedback.textContent = "Error loading question.";
            return;
        }

        // Display the question
        questionText.textContent = data.multiple_choice.question;

        // Correct option index
        const correctIndex = data.multiple_choice.correct_option_index;

        // Create option buttons
        data.multiple_choice.options.forEach((optionText, index) => {
            const button = document.createElement('button');
            button.className = 'optionButton';
            button.textContent = optionText;

            button.onclick = () => {
                // Disable all buttons after selection
                document.querySelectorAll('.optionButton').forEach(btn => btn.disabled = true);

                if (index === correctIndex) {
                    feedback.textContent = 'Correct!';
                    feedback.classList.add('correct');
                } else {
                    feedback.textContent = `Incorrect. The correct answer is "${data.multiple_choice.options[correctIndex]}".`;
                    feedback.classList.add('incorrect');
                }

                // Load the next question after a delay
                setTimeout(() => {
                    window.location.href = '/questions';
                }, 3000);
            };

            optionsContainer.appendChild(button);
        });
    } catch (error) {
        console.error("Error fetching multiple-choice question:", error);
        feedback.textContent = "Error loading question.";
    }
}

// Load the question on page load
window.onload = loadMultipleChoice;
