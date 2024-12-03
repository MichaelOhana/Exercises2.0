const questions = [
    {
        id: 'proficiency',
        text: "What is your current language proficiency?",
        options: [
            { value: 'beginner', label: 'Beginner' },
            { value: 'intermediate', label: 'Intermediate' },
            { value: 'advanced', label: 'Advanced' }
        ]
    },
    {
        id: 'struggle',
        text: "What do you struggle with more?",
        options: [
            { value: 'vocabulary', label: 'Vocabulary' },
            { value: 'grammar', label: 'Grammar' },
            { value: 'pronunciation', label: 'Pronunciation' }
        ]
    },
    {
        id: 'vocabulary_type',
        text: "What type of vocabulary would you like to learn?",
        options: [
            { value: 'everyday', label: 'Everyday English' },
            { value: 'business', label: 'Business English' },
            { value: 'academic', label: 'Academic English' },
            { value: 'industry', label: 'Industry-Specific' }
        ],
        followUps: {
            'business': {
                text: 'Which areas of business?',
                options: [
                    { value: 'marketing', label: 'Marketing' },
                    { value: 'sales', label: 'Sales' },
                    { value: 'finance', label: 'Finance' },
                    { value: 'management', label: 'Management' }
                ]
            },
            'academic': {
                text: 'Which academic fields?',
                options: [
                    { value: 'science', label: 'Science' },
                    { value: 'technology', label: 'Technology' },
                    { value: 'arts', label: 'Arts' },
                    { value: 'humanities', label: 'Humanities' }
                ]
            },
            'industry': {
                text: 'Which industry?',
                options: [
                    { value: 'medical', label: 'Medical' },
                    { value: 'legal', label: 'Legal' },
                    { value: 'technical', label: 'Technical' },
                    { value: 'other', label: 'Other' }
                ]
            }
        }
    },
    {
        id: 'main_goal',
        text: "What is your main goal for learning vocabulary?",
        options: [
            { value: 'work', label: 'Work/Professional Use' },
            { value: 'test', label: 'Passing a Test' },
            { value: 'conversation', label: 'Casual Conversation' },
            { value: 'reading_writing', label: 'Improving Reading/Writing Skills' }
        ]
    }
];

let currentQuestionIndex = 0;
let answers = {};

function updateUI() {
    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    
    // Update progress bar
    document.querySelector('.progress-bar').style.width = `${progress}%`;
    
    // Update question number
    document.getElementById('question-number').textContent = 
        `Question ${currentQuestionIndex + 1} of ${questions.length}`;
    
    // Update question text
    document.getElementById('question-text').textContent = currentQuestion.text;
    
    // Check if this is a follow-up question
    const isFollowUp = currentQuestion.isFollowUp;
    
    // Update options
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = currentQuestion.options.map(option => `
        <div class="option-item">
            <input type="radio" 
                   name="question" 
                   id="${option.value}" 
                   value="${option.value}"
                   ${answers[currentQuestion.id] === option.value ? 'checked' : ''}>
            <label for="${option.value}">${option.label}</label>
        </div>
    `).join('');
    
    // Update button states
    document.getElementById('prev-btn').disabled = currentQuestionIndex === 0;
    const nextBtn = document.getElementById('next-btn');
    nextBtn.textContent = currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next';
}

function handleNext() {
    const selectedOption = document.querySelector('input[name="question"]:checked');
    if (!selectedOption) {
        alert('Please select an option');
        return;
    }

    const currentQuestion = questions[currentQuestionIndex];
    answers[currentQuestion.id] = selectedOption.value;

    // Check if the current question has follow-ups
    if (currentQuestion.id === 'vocabulary_type' && currentQuestion.followUps?.[selectedOption.value]) {
        // Insert follow-up question after current question
        const followUp = currentQuestion.followUps[selectedOption.value];
        const followUpQuestion = {
            id: `${selectedOption.value}_followup`,
            text: followUp.text,
            options: followUp.options,
            isFollowUp: true
        };
        
        // Insert the follow-up question after the current question
        questions.splice(currentQuestionIndex + 1, 0, followUpQuestion);
    }

    if (currentQuestionIndex === questions.length - 1) {
        submitAnswers();
    } else {
        currentQuestionIndex++;
        updateUI();
    }
}

function handlePrevious() {
    if (currentQuestionIndex > 0) {
        // If current question is a follow-up, remove it when going back
        const currentQuestion = questions[currentQuestionIndex];
        if (currentQuestion.isFollowUp) {
            questions.splice(currentQuestionIndex, 1);
        }
        currentQuestionIndex--;
        updateUI();
    }
}

async function submitAnswers() {
    try {
        const response = await fetch('/submit-questionnaire', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(answers)
        });

        if (response.ok) {
            window.location.href = '/generating-course';
        } else {
            alert('There was an error submitting your answers. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('There was an error submitting your answers. Please try again.');
    }
}

// Add event listeners
document.getElementById('next-btn').addEventListener('click', handleNext);
document.getElementById('prev-btn').addEventListener('click', handlePrevious);

// Initialize the UI
updateUI(); 