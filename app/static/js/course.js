document.addEventListener('DOMContentLoaded', function() {
    const courseNav = document.getElementById('courseNav');
    const toggleNav = document.getElementById('toggleNav');
    const contentDisplay = document.getElementById('contentDisplay');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const navContent = document.querySelector('.nav-content');
    const navHeader = document.querySelector('.nav-header h2');

    // Toggle navigation menu
    toggleNav.addEventListener('click', () => {
        const isCollapsed = courseNav.classList.toggle('collapsed');
        
        if (isCollapsed) {
            navContent.style.display = 'none';
            navHeader.style.display = 'none';
        } else {
            // Use setTimeout to ensure the width transition happens first
            setTimeout(() => {
                navContent.style.display = 'block';
                navHeader.style.display = 'block';
            }, 150); // Half of the transition time
        }
    });

    // Handle unit expansion
    document.querySelectorAll('.unit-header').forEach(header => {
        header.addEventListener('click', () => {
            const items = header.nextElementSibling;
            const toggle = header.querySelector('.unit-toggle');
            items.classList.toggle('expanded');
            toggle.textContent = items.classList.contains('expanded') ? '▼' : '▶';
        });
    });

    // Handle content loading
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', async () => {
            const type = item.dataset.type;
            const id = item.dataset.id;
            
            try {
                const response = await fetch(`/api/content/${type}/${id}`);
                const content = await response.json();
                
                // Display content based on type
                displayContent(type, content);
                
                // Update navigation state
                updateNavigationState(item);
            } catch (error) {
                console.error('Error loading content:', error);
                contentDisplay.innerHTML = 'Error loading content';
            }
        });
    });

    function displayContent(type, content) {
        let html = '';
        
        switch(type) {
            case 'lesson':
                html = `
                    <h1>${content.title}</h1>
                    <div class="introduction">${content.introduction}</div>
                    <div class="main-content">${content.content}</div>
                    <div class="summary">${content.summary}</div>
                `;
                break;
            case 'exercise':
                html = `
                    <h1>${content.title}</h1>
                    <div class="instructions">${content.instructions}</div>
                    <div class="questions">
                        ${content.questions.map(q => `<div class="question">${q}</div>`).join('')}
                    </div>
                `;
                break;
            case 'quiz':
                html = `
                    <h1>${content.title}</h1>
                    <div class="questions">
                        ${content.questions.map((q, i) => `
                            <div class="question">
                                <p>${q.question}</p>
                                <div class="options">
                                    ${q.options.map((opt, j) => `
                                        <label>
                                            <input type="radio" name="q${i}" value="${j}">
                                            ${opt}
                                        </label>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                break;
        }
        
        contentDisplay.innerHTML = html;
    }

    // Function to update active menu item
    function updateActiveMenuItem(item) {
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        // Add active class to current item
        item.classList.add('active');
        
        // Ensure the parent unit is expanded
        const parentUnit = item.closest('.unit-items');
        if (parentUnit && !parentUnit.classList.contains('expanded')) {
            parentUnit.classList.add('expanded');
            const toggle = parentUnit.previousElementSibling.querySelector('.unit-toggle');
            toggle.textContent = '▼';
        }
    }

    // Update the updateNavigationState function
    function updateNavigationState(currentItem) {
        const allItems = Array.from(document.querySelectorAll('.nav-item'));
        const currentIndex = allItems.indexOf(currentItem);
        
        prevButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === allItems.length - 1;
        
        // Update active state in menu
        updateActiveMenuItem(currentItem);
        
        // Store current position
        localStorage.setItem('currentContentIndex', currentIndex);
    }

    // Update the navigation button handlers
    prevButton.addEventListener('click', () => {
        const currentIndex = parseInt(localStorage.getItem('currentContentIndex'));
        if (currentIndex > 0) {
            const allItems = document.querySelectorAll('.nav-item');
            const prevItem = allItems[currentIndex - 1];
            prevItem.click();  // This will trigger the content load and updateNavigationState
        }
    });

    nextButton.addEventListener('click', () => {
        const currentIndex = parseInt(localStorage.getItem('currentContentIndex'));
        const allItems = document.querySelectorAll('.nav-item');
        if (currentIndex < allItems.length - 1) {
            const nextItem = allItems[currentIndex + 1];
            nextItem.click();  // This will trigger the content load and updateNavigationState
        }
    });
}); 