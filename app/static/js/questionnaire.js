const ALL_LANGUAGES = [
    'Afrikaans', 'Albanian', 'Amharic', 'Arabic', 'Armenian', 'Assamese', 'Aymara', 
    'Azerbaijani', 'Balochi', 'Bamanankan', 'Bashkir', 'Basque', 'Belarusian', 
    'Bengali', 'Bhojpuri', 'Bikol', 'Bosnian', 'Bulgarian', 'Burmese', 'Cantonese', 
    'Catalan', 'Cebuano', 'Chechen', 'Cherokee', 'Chichewa', 'Chinese (Mandarin)', 
    'Chuvash', 'Cornish', 'Corsican', 'Croatian', 'Czech', 'Danish', 'Dari', 
    'Dholuo', 'Dutch', 'Dzongkha', 'English', 'Esperanto', 'Estonian', 'Ewe', 
    'Faroese', 'Fijian', 'Filipino', 'Finnish', 'French', 'Galician', 'Georgian', 
    'German', 'Greek', 'Greenlandic', 'Guarani', 'Gujarati', 'Haitian Creole', 
    'Hausa', 'Hawaiian', 'Hebrew', 'Hindi', 'Hmong', 'Hungarian', 'Icelandic', 
    'Igbo', 'Ilocano', 'Indonesian', 'Inuktitut', 'Irish', 'Italian', 'Japanese', 
    'Javanese', 'Kannada', 'Kashmiri', 'Kazakh', 'Khmer', 'Kinyarwanda', 'Kirundi', 
    'Korean', 'Kurdish', 'Kyrgyz', 'Lao', 'Latvian', 'Lingala', 'Lithuanian', 
    'Luxembourgish', 'Macedonian', 'Malagasy', 'Malay', 'Malayalam', 'Maltese', 
    'Maori', 'Marathi', 'Mongolian', 'Nahuatl', 'Navajo', 'Nepali', 'Norwegian', 
    'Odia', 'Oromo', 'Pashto', 'Persian', 'Polish', 'Portuguese', 'Punjabi', 
    'Quechua', 'Romanian', 'Russian', 'Samoan', 'Sanskrit', 'Serbian', 'Shona', 
    'Sindhi', 'Sinhala', 'Slovak', 'Slovene', 'Somali', 'Spanish', 'Swahili', 
    'Swedish', 'Tajik', 'Tamil', 'Tatar', 'Telugu'
].sort();

const questions = [
    {
        id: 'native_language',
        text: "What is your native language?",
        type: 'dropdown',
        options: [
            { value: 'english', label: 'English' },
            { value: 'spanish', label: 'Spanish' },
            { value: 'chinese', label: 'Chinese (Mandarin)' },
            { value: 'french', label: 'French' },
            { value: 'german', label: 'German' },
            { value: 'other', label: 'Other' }
        ],
        allLanguages: ALL_LANGUAGES
    },
    {
        id: 'target_language',
        text: "What language do you want to learn?",
        type: 'dropdown',
        options: [
            { value: 'english', label: 'English' },
            { value: 'spanish', label: 'Spanish' },
            { value: 'chinese', label: 'Chinese (Mandarin)' },
            { value: 'french', label: 'French' },
            { value: 'german', label: 'German' },
            { value: 'other', label: 'Other' }
        ],
        allLanguages: ALL_LANGUAGES
    },
    {
        id: 'current_level',
        text: "Do you know any [selected language]?",
        type: 'radio',
        options: [
            { value: 'none', label: 'Not at all' },
            { value: 'little', label: 'A little' },
            { value: 'basic', label: 'Basic conversations' },
            { value: 'comfortable', label: 'Comfortable with most conversations' },
            { value: 'fluent', label: 'Fluent' }
        ]
    },
    {
        id: 'struggles',
        text: "What do you struggle with most?",
        type: 'checkbox',
        maxSelections: 2,
        options: [
            { value: 'speaking', label: 'Speaking' },
            { value: 'understanding', label: 'Understanding' },
            { value: 'reading', label: 'Reading' },
            { value: 'writing', label: 'Writing' }
        ],
        followUps: {
            'speaking': {
                id: 'speaking_struggles',
                text: 'What do you struggle with most with Speaking?',
                type: 'checkbox',
                maxSelections: 3,
                options: [
                    { value: 'meetings', label: 'Meetings' },
                    { value: 'clients', label: 'Talking to clients/customers' },
                    { value: 'presentations', label: 'Presentations' },
                    { value: 'informal', label: 'Informal conversations with colleagues' },
                    { value: 'native_speakers', label: 'Talking to native speakers' },
                    { value: 'technical', label: 'Explaining technical or complex ideas' },
                    { value: 'other', label: 'Other', allowText: true }
                ]
            },
            'understanding': {
                id: 'understanding_struggles',
                text: 'What do you struggle with most with Understanding?',
                type: 'checkbox',
                maxSelections: 3,
                options: [
                    { value: 'fast_speakers', label: 'Understanding fast speakers' },
                    { value: 'meetings', label: 'Following conversations in meetings' },
                    { value: 'presentations', label: 'Following presentations or lectures' },
                    { value: 'accents', label: 'Understanding accents or dialects' },
                    { value: 'informal', label: 'Understanding informal, casual speech' },
                    { value: 'other', label: 'Other', allowText: true }
                ]
            },
            'reading': {
                id: 'reading_struggles',
                text: 'What do you struggle with most with Reading?',
                type: 'checkbox',
                maxSelections: 3,
                options: [
                    { value: 'technical', label: 'Reading professional or technical documents' },
                    { value: 'emails', label: 'Reading emails or reports' },
                    { value: 'slang', label: 'Understanding slang or informal writing' },
                    { value: 'grammar', label: 'Understanding complex grammar or sentence structure' },
                    { value: 'long_texts', label: 'Keeping up with long texts' },
                    { value: 'other', label: 'Other', allowText: true }
                ]
            },
            'writing': {
                id: 'writing_struggles',
                text: 'What do you struggle with most with Writing?',
                type: 'checkbox',
                maxSelections: 3,
                options: [
                    { value: 'emails', label: 'Writing professional emails' },
                    { value: 'reports', label: 'Writing reports or documents' },
                    { value: 'grammar', label: 'Using the correct grammar and sentence structure' },
                    { value: 'vocabulary', label: 'Finding the right words or vocabulary' },
                    { value: 'informal', label: 'Writing informally or casually' },
                    { value: 'other', label: 'Other', allowText: true }
                ]
            }
        }
    },
    {
        id: 'job_area',
        text: "What is your job or area of expertise?",
        type: 'dropdown',
        options: [
            { value: 'business', label: 'Business' },
            { value: 'technology', label: 'Technology' },
            { value: 'medicine', label: 'Medicine' },
            { value: 'education', label: 'Education' },
            { value: 'arts', label: 'Arts' },
            { value: 'science', label: 'Science' },
            { value: 'legal', label: 'Legal' },
            { value: 'engineering', label: 'Engineering' },
            { value: 'marketing_sales', label: 'Marketing and Sales' },
            { value: 'finance', label: 'Finance' },
            { value: 'hospitality', label: 'Hospitality' },
            { value: 'other', label: 'Other', allowText: true }
        ],
        followUps: {
            'business': {
                text: "What is your role in business?",
                type: 'dropdown',
                options: [
                    { value: 'manager', label: 'Manager' },
                    { value: 'salesperson', label: 'Salesperson' },
                    { value: 'consultant', label: 'Consultant' },
                    { value: 'entrepreneur', label: 'Entrepreneur' },
                    { value: 'analyst', label: 'Analyst' },
                    { value: 'other', label: 'Other', allowText: true }
                ]
            },
            // ... similar followUps for other job areas
        }
    },
    {
        id: 'confidence_situations',
        text: "Which situations do you want to feel more confident using [selected language] in?",
        type: 'checkbox',
        maxSelections: 4,
        options: [
            { value: 'meetings', label: 'Meetings' },
            { value: 'presentations', label: 'Presentations' },
            { value: 'emails', label: 'Writing emails or reports' },
            { value: 'socializing', label: 'Socializing with colleagues' },
            { value: 'clients', label: 'Talking to clients/customers' },
            { value: 'networking', label: 'Networking events' },
            { value: 'interviews', label: 'Job interviews' },
            { value: 'negotiations', label: 'Negotiations' },
            { value: 'other', label: 'Other', allowText: true }
        ]
    },
    {
        id: 'learning_preferences',
        text: "How do you prefer to learn?",
        type: 'checkbox',
        maxSelections: 3,
        options: [
            { value: 'reading_writing', label: 'Reading and writing exercises' },
            { value: 'audio', label: 'Listening to audio lessons' },
            { value: 'videos', label: 'Watching videos' },
            { value: 'conversations', label: 'Practicing conversations' },
            { value: 'quizzes', label: 'Interactive quizzes' },
            { value: 'simulations', label: 'Simulated environments', tooltip: 'Simulated environments include practice scenarios like meetings, negotiations, phone calls, and other real-life interactions.' },
            { value: 'other', label: 'Other', allowText: true }
        ]
    },
    {
        id: 'specific_topics',
        text: "Do you have any specific vocabulary or topics you want to focus on?",
        type: 'text',
        optional: true,
        placeholder: 'Examples: industry-specific terms, common business phrases, academic topics...',
        tooltip: 'This helps us customize your learning experience with relevant vocabulary and topics.'
    }
];

let currentQuestionIndex = 0;
let answers = {};
let followUpQueue = [];
let parentQuestionIndex = null;
let currentFollowUp = null;

function updateUI() {
    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
    
    document.querySelector('.progress-bar').style.width = `${progress}%`;
    document.getElementById('question-number').textContent = 
        `Question ${currentQuestionIndex + 1} of ${questions.length}`;
    
    let questionText = currentQuestion.text;
    if (questionText.includes('[selected language]')) {
        const targetLanguage = answers.target_language;
        questionText = questionText.replace('[selected language]', targetLanguage || '');
    }
    
    document.getElementById('question-text').textContent = questionText;
    
    renderQuestionOptions(currentQuestion);
    
    document.getElementById('prev-btn').disabled = currentQuestionIndex === 0;
    const nextBtn = document.getElementById('next-btn');
    nextBtn.textContent = currentQuestionIndex === questions.length - 1 ? 'Submit' : 'Next';
}

function renderQuestionOptions(question) {
    const container = document.getElementById('options-container');
    container.innerHTML = '';

    switch(question.type) {
        case 'dropdown':
            renderDropdown(question, container);
            break;
        case 'radio':
            renderRadioOptions(question, container);
            break;
        case 'checkbox':
            renderCheckboxOptions(question, container);
            break;
        case 'text':
            renderTextInput(question, container);
            break;
    }
}

function renderDropdown(question, container) {
    const wrapper = document.createElement('div');
    wrapper.className = 'dropdown-wrapper';

    const select = document.createElement('select');
    select.className = 'form-select';
    select.id = question.id;

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select an option';
    defaultOption.disabled = true;
    defaultOption.selected = !answers[question.id];
    select.appendChild(defaultOption);

    question.options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.label;
        optionElement.selected = answers[question.id] === option.value;
        select.appendChild(optionElement);
    });

    select.addEventListener('change', (e) => {
        if (e.target.value === 'other' && question.allLanguages) {
            // Remove the regular dropdown and show the searchable language dropdown
            wrapper.innerHTML = '';
            renderSearchableLanguageDropdown(question, wrapper);
        } else {
            answers[question.id] = e.target.value;
        }
    });

    wrapper.appendChild(select);
    container.appendChild(wrapper);

    // If 'other' was previously selected, show the searchable dropdown
    if (answers[question.id] === 'other' && question.allLanguages) {
        wrapper.innerHTML = '';
        renderSearchableLanguageDropdown(question, wrapper);
    }
}

function renderSearchableLanguageDropdown(question, container) {
    const wrapper = document.createElement('div');
    wrapper.className = 'searchable-dropdown';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control';
    input.placeholder = 'Type to search language...';

    const dropdown = document.createElement('select');
    dropdown.className = 'form-select';
    dropdown.size = 10; // Show 10 options at a time

    function updateOptions(searchText = '') {
        dropdown.innerHTML = '';
        const filteredLanguages = question.allLanguages.filter(lang => 
            lang.toLowerCase().includes(searchText.toLowerCase())
        );

        filteredLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.toLowerCase().replace(/\s+/g, '_');
            option.textContent = lang;
            option.selected = answers[question.id] === option.value;
            dropdown.appendChild(option);
        });
    }

    input.addEventListener('input', (e) => {
        updateOptions(e.target.value);
    });

    dropdown.addEventListener('change', (e) => {
        const selectedOption = e.target.options[e.target.selectedIndex];
        // Store the original language name instead of the lowercase underscore version
        answers[question.id] = selectedOption.textContent;
        input.value = selectedOption.textContent;
    });

    const backButton = document.createElement('button');
    backButton.className = 'btn btn-outline-secondary mt-2';
    backButton.textContent = 'Back to main options';
    backButton.addEventListener('click', () => {
        container.innerHTML = '';
        renderDropdown(question, container);
    });

    wrapper.appendChild(input);
    wrapper.appendChild(dropdown);
    wrapper.appendChild(backButton);
    container.appendChild(wrapper);

    updateOptions();
}

function renderRadioOptions(question, container) {
    const radioGroup = document.createElement('div');
    radioGroup.className = 'radio-group';

    question.options.forEach(option => {
        const wrapper = document.createElement('div');
        wrapper.className = 'option-item';

        const input = document.createElement('input');
        input.type = 'radio';
        input.id = `${question.id}_${option.value}`;
        input.name = question.id;
        input.value = option.value;
        input.checked = answers[question.id] === option.value;

        const label = document.createElement('label');
        label.htmlFor = input.id;
        label.textContent = option.label;

        input.addEventListener('change', () => {
            answers[question.id] = option.value;
        });

        wrapper.appendChild(input);
        wrapper.appendChild(label);
        radioGroup.appendChild(wrapper);
    });

    container.appendChild(radioGroup);
}

function renderCheckboxOptions(question, container) {
    const checkboxGroup = document.createElement('div');
    checkboxGroup.className = 'checkbox-group';

    if (question.maxSelections) {
        const hint = document.createElement('small');
        hint.className = 'text-muted';
        hint.textContent = `Select up to ${question.maxSelections} options`;
        container.appendChild(hint);
    }

    question.options.forEach(option => {
        const wrapper = document.createElement('div');
        wrapper.className = 'option-item';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = `${question.id}_${option.value}`;
        input.value = option.value;
        input.checked = answers[question.id]?.includes(option.value);

        const label = document.createElement('label');
        label.htmlFor = input.id;
        label.textContent = option.label;

        if (option.tooltip) {
            const tooltip = document.createElement('span');
            tooltip.className = 'tooltip-icon';
            tooltip.title = option.tooltip;
            tooltip.textContent = 'ⓘ';
            label.appendChild(tooltip);
        }

        input.addEventListener('change', () => {
            const selectedOptions = Array.from(checkboxGroup.querySelectorAll('input:checked'))
                .map(input => input.value);
                
            if (selectedOptions.length > question.maxSelections) {
                input.checked = false;
                return;
            }

            answers[question.id] = selectedOptions;

            // Handle "Other" text input
            if (option.value === 'other' && option.allowText) {
                const otherInputId = `${question.id}_other_text`;
                const existingInput = document.getElementById(otherInputId);
                
                if (input.checked && !existingInput) {
                    const textWrapper = document.createElement('div');
                    textWrapper.className = 'other-text-input';
                    
                    const textInput = document.createElement('input');
                    textInput.type = 'text';
                    textInput.id = otherInputId;
                    textInput.className = 'form-control mt-2';
                    textInput.placeholder = 'Please specify';
                    textInput.value = answers[otherInputId] || '';
                    
                    textInput.addEventListener('input', (e) => {
                        answers[otherInputId] = e.target.value;
                    });
                    
                    textWrapper.appendChild(textInput);
                    wrapper.appendChild(textWrapper);
                } else if (!input.checked && existingInput) {
                    existingInput.parentElement.remove();
                    delete answers[otherInputId];
                }
            }
        });

        wrapper.appendChild(input);
        wrapper.appendChild(label);
        checkboxGroup.appendChild(wrapper);

        // Re-add the text input if "other" was previously selected
        if (option.value === 'other' && option.allowText && input.checked) {
            const otherInputId = `${question.id}_other_text`;
            const textWrapper = document.createElement('div');
            textWrapper.className = 'other-text-input';
            
            const textInput = document.createElement('input');
            textInput.type = 'text';
            textInput.id = otherInputId;
            textInput.className = 'form-control mt-2';
            textInput.placeholder = 'Please specify';
            textInput.value = answers[otherInputId] || '';
            
            textInput.addEventListener('input', (e) => {
                answers[otherInputId] = e.target.value;
            });
            
            textWrapper.appendChild(textInput);
            wrapper.appendChild(textWrapper);
        }
    });

    container.appendChild(checkboxGroup);
}

function renderTextInput(question, container, isFollowUp = false) {
    const wrapper = document.createElement('div');
    wrapper.className = isFollowUp ? 'follow-up-input' : 'text-input-wrapper';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control';
    input.id = question.id;
    input.placeholder = question.placeholder || '';
    input.value = answers[question.id] || '';

    input.addEventListener('input', (e) => {
        answers[question.id] = e.target.value;
    });

    if (question.tooltip) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-text';
        tooltip.textContent = question.tooltip;
        wrapper.appendChild(tooltip);
    }

    wrapper.appendChild(input);
    container.appendChild(wrapper);
}

function handleNext() {
    const currentQuestion = currentFollowUp || questions[currentQuestionIndex];
    
    if (!validateAnswer(currentQuestion)) {
        return;
    }

    currentFollowUp = null;

    if (currentQuestion.id === 'struggles' && !currentQuestion.isFollowUp) {
        const selectedOptions = answers[currentQuestion.id];
        if (Array.isArray(selectedOptions) && selectedOptions.length > 0) {
            parentQuestionIndex = currentQuestionIndex;
            
            followUpQueue = selectedOptions
                .filter(option => currentQuestion.followUps[option])
                .map(option => ({
                    ...currentQuestion.followUps[option],
                    parentId: currentQuestion.id,
                    parentOption: option,
                    isFollowUp: true,
                    id: `${currentQuestion.id}_${option}_followup`
                }));

            if (followUpQueue.length > 0) {
                const followUp = followUpQueue.shift();
                renderFollowUpQuestion(followUp);
                return;
            }
        }
    }

    if (followUpQueue.length > 0) {
        const followUp = followUpQueue.shift();
        renderFollowUpQuestion(followUp);
        return;
    }

    if (currentQuestionIndex === questions.length - 1) {
        submitAnswers();
    } else {
        currentQuestionIndex++;
        parentQuestionIndex = null;
        updateUI();
    }
}

function handlePrevious() {
    if (parentQuestionIndex !== null) {
        currentFollowUp = null;
        currentQuestionIndex = parentQuestionIndex;
        followUpQueue = [];
        parentQuestionIndex = null;
        updateUI();
    } else if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        updateUI();
    }
}

function validateAnswer(question) {
    const questionToValidate = currentFollowUp || question;
    const answer = answers[questionToValidate.id];
    
    if (questionToValidate.optional) {
        return true;
    }

    if (!answer || (Array.isArray(answer) && answer.length === 0)) {
        alert('Please answer the question before proceeding.');
        return false;
    }

    // For checkbox questions with "other" option
    if (Array.isArray(answer) && answer.includes('other')) {
        const otherText = answers[`${questionToValidate.id}_other_text`];
        if (!otherText) {
            alert('Please specify your "Other" option.');
            return false;
        }
    }

    return true;
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

function renderFollowUpQuestion(followUp) {
    const container = document.getElementById('options-container');
    container.innerHTML = '';

    currentFollowUp = followUp;

    const progress = ((parentQuestionIndex + 1) / questions.length) * 100;
    document.querySelector('.progress-bar').style.width = `${progress}%`;

    document.getElementById('question-number').textContent = 
        `Question ${parentQuestionIndex + 1} - Follow-up`;

    document.getElementById('question-text').textContent = followUp.text;

    renderQuestionOptions(followUp);
}

// Add event listeners
document.getElementById('next-btn').addEventListener('click', handleNext);
document.getElementById('prev-btn').addEventListener('click', handlePrevious);

// Make sure the initialization happens after the DOM is loaded:
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the UI
    updateUI();
});