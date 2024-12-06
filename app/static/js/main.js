// Navigation state
let isNavigationOpen = true;

// Toggle navigation
function toggleNavigation() {
    const nav = document.getElementById('course-navigation');
    const toggleBtn = nav.querySelector('.toggle-button');
    isNavigationOpen = !isNavigationOpen;
    
    if (isNavigationOpen) {
        nav.classList.remove('closed');
        toggleBtn.textContent = '←';
    } else {
        nav.classList.add('closed');
        toggleBtn.textContent = '→';
    }
}

// Load course structure
async function loadCourseStructure() {
    try {
        const response = await fetch('/api/course-structure');
        const data = await response.json();
        renderNavigation(data);
    } catch (error) {
        console.error('Error loading course structure:', error);
    }
}

// Render navigation
function renderNavigation(data) {
    const navContent = document.querySelector('.nav-content');
    navContent.innerHTML = data.units.map(unit => `
        <div class="unit">
            <h3>${unit.title}</h3>
            <div class="unit-content">
                ${unit.content.map(item => `
                    <div class="content-item" onclick="loadContent('${item.type}', '${item.id}')">
                        ${item.title}
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// Load content
function loadContent(type, id) {
    const contentDisplay = document.getElementById('content-display');
    
    // This is a simple template - you can expand it based on your needs
    switch (type) {
        case 'lesson':
            contentDisplay.innerHTML = createLessonTemplate(id);
            break;
        case 'exercise':
            contentDisplay.innerHTML = createExerciseTemplate(id);
            break;
        case 'quiz':
            contentDisplay.innerHTML = createQuizTemplate(id);
            break;
    }
}

// Content templates
function createLessonTemplate(id) {
    return `
        <div class="lesson-template">
            <h1>Lesson Title</h1>
            <div class="content">
                <section>
                    <h2>Introduction</h2>
                    <p>Lesson introduction goes here...</p>
                </section>
                
                <section>
                    <h2>Main Content</h2>
                    <p>Main lesson content goes here...</p>
                </section>
                
                <section>
                    <h2>Summary</h2>
                    <p>Lesson summary goes here...</p>
                </section>
            </div>
            <button onclick="navigateNext()">Next Lesson</button>
        </div>
    `;
}

function createExerciseTemplate(id) {
    return `
        <div class="exercise-template">
            <h1>Exercise Title</h1>
            <div class="content">
                <section>
                    <h2>Instructions</h2>
                    <p>Exercise instructions go here...</p>
                </section>
                
                <section>
                    <h2>Your Task</h2>
                    <p>Exercise content goes here...</p>
                </section>
            </div>
            <button onclick="navigateNext()">Next Exercise</button>
        </div>
    `;
}

function createQuizTemplate(id) {
    return `
        <div class="quiz-template">
            <h1>Quiz Title</h1>
            <div class="content">
                <section>
                    <h2>Question 1</h2>
                    <div>
                        <label>
                            <input type="radio" name="q1" value="a"> Option A
                        </label>
                        <label>
                            <input type="radio" name="q1" value="b"> Option B
                        </label>
                        <label>
                            <input type="radio" name="q1" value="c"> Option C
                        </label>
                    </div>
                </section>
            </div>
            <button onclick="submitQuiz()">Submit Quiz</button>
        </div>
    `;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCourseStructure();
}); 