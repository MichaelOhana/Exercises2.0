const submitBtn = document.getElementById('submitBtn');
const feedback = document.getElementById('feedback');
const sentenceText = document.getElementById('sentenceText'); // Ensure we are correctly selecting the element

// Fetch fill-in-the-blank question from the backend
async function loadFillInTheBlank() {
    try {
        const response = await fetch('http://127.0.0.1:5000/get-fill-in-the-blank');
        let data = await response.json();

        // Check if data is a string; if so, parse it to JSON
        if (typeof data === 'string') {
            data = JSON.parse(data);
        }

        // Log data to verify structure is as expected
        console.log("Fetched data:", data);

        // Ensure that data has the expected properties
        if (!data.sentence || !data.correct_fill) {
            console.error("Data is missing 'sentence' or 'correct_fill' properties:", data);
            return;
        }

        // Replace the placeholder "__" in the sentence with an input element
        const sentenceWithInput = data.sentence.replace("__", '<input type="text" id="userInput" placeholder="Type your answer here">');
        
        // Log to confirm the modified sentence
        console.log("Modified sentence:", sentenceWithInput);

        // Update the sentenceText element with the modified sentence
        sentenceText.innerHTML = sentenceWithInput;

        // Store the correct answer for checking on submit
        const correctAnswer = data.correct_fill.toLowerCase();

        // Add event listener for submit button
        submitBtn.addEventListener('click', () => {
            const userInputValue = document.getElementById('userInput').value.trim().toLowerCase();
            document.getElementById('userInput').disabled = true;
            submitBtn.disabled = true;

            if (userInputValue === correctAnswer) {
                feedback.textContent = `Correct! "${correctAnswer.charAt(0).toUpperCase() + correctAnswer.slice(1)}" is the right answer.`;
                feedback.classList.add('correct');
            } else {
                feedback.textContent = `Incorrect. The correct answer is "${correctAnswer}".`;
                feedback.classList.add('incorrect');
            }
        });
    } catch (error) {
        console.error("Error fetching fill-in-the-blank question:", error);
    }
}

// Load the fill-in-the-blank question on page load
window.onload = loadFillInTheBlank;
