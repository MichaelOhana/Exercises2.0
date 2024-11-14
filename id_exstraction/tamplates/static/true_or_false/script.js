const trueBtn = document.getElementById('trueBtn');
const falseBtn = document.getElementById('falseBtn');
const feedback = document.getElementById('feedback');

// Set the correct answer ('true' or 'false')
const correctAnswer = 'true';

trueBtn.addEventListener('click', () => {
    handleAnswer('true');
});

falseBtn.addEventListener('click', () => {
    handleAnswer('false');
});

function handleAnswer(selectedAnswer) {
    // Disable buttons after selection
    trueBtn.disabled = true;
    falseBtn.disabled = true;

    if (selectedAnswer === correctAnswer) {
        feedback.textContent = 'Correct! Mitochondria are indeed known as the powerhouses of the cell.';
        feedback.classList.add('correct');
    } else {
        feedback.textContent = 'Incorrect. Mitochondria are the powerhouses of the cell because they generate most of the cell\'s ATP.';
        feedback.classList.add('incorrect');
    }
}
