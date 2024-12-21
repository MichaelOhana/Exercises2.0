document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM Content Loaded');

    const container = document.querySelector('.swipe-container');
    const cards = Array.from(document.querySelectorAll('.word-card'));
    const totalCards = cards.length;
    let currentIndex = 0;

    console.log('Found cards:', cards.length);

    // Initialize progress bar
    updateProgress();

    cards.forEach((card, index) => {
        console.log('Initializing card:', index);

        if (index !== 0) {
            card.style.display = 'none';
        }

        // Click to flip
        card.addEventListener('click', (e) => {
            console.log('Card clicked');
            card.classList.toggle('flipped');
        });

        // Initialize Hammer.js
        if (typeof Hammer !== 'undefined') {
            console.log('Hammer.js is loaded');
            const hammer = new Hammer(card);
            hammer.get('pan').set({ direction: Hammer.DIRECTION_HORIZONTAL });
            hammer.on('pan', handlePan);
            hammer.on('panend', handlePanEnd);
        } else {
            console.error('Hammer.js is not loaded!');
        }
    });

    function handlePan(event) {
        console.log('Pan event:', event.deltaX);
        const card = cards[currentIndex];
        const threshold = 100;

        if (!card.classList.contains('flipped')) {
            card.style.transition = 'none';
            card.style.transform = `translateX(${event.deltaX}px) rotate(${event.deltaX * 0.1}deg)`;

            if (event.deltaX > threshold) {
                card.style.backgroundColor = '#d4edda';
            } else if (event.deltaX < -threshold) {
                card.style.backgroundColor = '#f8d7da';
            } else {
                card.style.backgroundColor = 'white';
            }
        }
    }

    function handlePanEnd(event) {
        console.log('Pan end event:', event.deltaX);
        const card = cards[currentIndex];
        const threshold = 100;

        if (!card.classList.contains('flipped')) {
            card.style.transition = 'transform 0.3s';

            if (Math.abs(event.deltaX) > threshold) {
                const direction = event.deltaX > 0 ? 1 : -1;
                card.style.transform = `translateX(${direction * window.innerWidth}px) rotate(${direction * 90}deg)`;
                handleSwipe(direction > 0);
            } else {
                card.style.transform = '';
                card.style.backgroundColor = 'white';
            }
        }
    }

    function handleSwipe(isRight) {
        console.log('Handling swipe:', isRight ? 'right' : 'left');
        const card = cards[currentIndex];

        // Save the result
        const word = card.querySelector('.word-text').textContent;
        saveResult(word, isRight);

        // Animate card off screen
        const direction = isRight ? 1 : -1;
        card.style.transition = 'transform 0.5s';
        card.style.transform = `translateX(${direction * window.innerWidth}px) rotate(${direction * 90}deg)`;

        setTimeout(() => {
            card.style.display = 'none';
            currentIndex++;
            updateProgress();

            if (currentIndex < totalCards) {
                const nextCard = cards[currentIndex];
                nextCard.style.display = 'block';
                nextCard.style.transform = '';
                nextCard.style.backgroundColor = 'white';
            } else {
                showCompletionMessage();
            }
        }, 500);
    }

    function updateProgress() {
        const progress = (currentIndex / totalCards) * 100;
        document.querySelector('.progress').style.width = `${progress}%`;
    }

    function showCompletionMessage() {
        // Clear everything in the container
        container.innerHTML = `
            <div class="completion-message">
                <p>You've completed the word assessment.</p>
                <div class="loading-animation">
                    <div class="spinner"></div>
                    <div class="generation-status">Analyzing your responses...</div>
                </div>
            </div>
        `;

        // Hide the buttons and progress bar
        document.querySelector('.swipe-buttons').style.display = 'none';
        document.querySelector('.progress-bar').style.display = 'none';

        // Hide the header text
        const headerElements = document.querySelectorAll('h1, .text-muted');
        headerElements.forEach(el => el.style.display = 'none');

        // Array of generation steps
        const generationSteps = [
            "Analyzing your responses...",
            "Identifying knowledge gaps...",
            "Creating personalized exercises...",
            "Generating vocabulary lessons...",
            "Preparing practice materials...",
            "Finalizing your course structure...",
            "Almost ready..."
        ];

        let currentStep = 0;
        const statusElement = document.querySelector('.generation-status');

        // Update status message every 800ms
        const statusInterval = setInterval(() => {
            currentStep = (currentStep + 1) % generationSteps.length;
            statusElement.style.opacity = 0;

            setTimeout(() => {
                statusElement.textContent = generationSteps[currentStep];
                statusElement.style.opacity = 1;
            }, 200);
        }, 2000);

        // Redirect after all steps are shown
        setTimeout(() => {
            clearInterval(statusInterval);
            window.location.href = '/course/default';
        }, generationSteps.length * 2000 + 1000);
    }

    function saveResult(word, isKnown) {
        console.log('Saving result:', word, isKnown);
        fetch('/submit-assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                word: word,
                known: isKnown
            })
        }).catch(error => console.error('Error saving result:', error));
    }

    // Button controls
    window.swipeLeft = function () {
        console.log('Swipe left button clicked');
        if (!cards[currentIndex].classList.contains('flipped')) {
            handleSwipe(false);
        }
    };

    window.swipeRight = function () {
        console.log('Swipe right button clicked');
        if (!cards[currentIndex].classList.contains('flipped')) {
            handleSwipe(true);
        }
    };
}); 