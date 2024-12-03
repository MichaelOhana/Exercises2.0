// script.js
document.getElementById("quiz-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form submission
  
    // Capture quiz responses
    const level = document.getElementById("level").value;
    const reason = document.getElementById("reason").value;
    const interest = document.getElementById("interest").value;
  
    // Display the results
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = `
      <p>Thank you for completing the quiz!</p>
      <p><strong>Level:</strong> ${level}</p>
      <p><strong>Reason:</strong> ${reason}</p>
      <p><strong>Interest:</strong> ${interest}</p>
    `;
  
    // Optional: Send data to a server
    // fetch('/submit-quiz', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({ level, reason, interest })
    // }).then(response => {
    //   console.log('Quiz submitted successfully!');
    // }).catch(error => {
    //   console.error('Error submitting quiz:', error);
    // });
  });
  