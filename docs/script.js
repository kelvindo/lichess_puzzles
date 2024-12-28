let puzzles = [];
let currentPuzzleIndex = 0;
const storageKey = `currentPuzzleIndex_${PUZZLE_PACK}`;

async function loadPuzzles() {
    try {
        const response = await fetch(`../static_puzzles/${PUZZLE_PACK}`);
        const csvText = await response.text();
        
        // Parse CSV
        const lines = csvText.split('\n');
        const headers = lines[0].split(',');
        
        // Convert CSV to array of objects
        puzzles = lines.slice(1).filter(line => line.trim()).map(line => {
            const values = line.split(',');
            const puzzle = {};
            headers.forEach((header, index) => {
                puzzle[header.trim()] = values[index]?.trim();
            });
            return puzzle;
        });

        // Load last position from localStorage using pack-specific key
        const savedIndex = localStorage.getItem(storageKey);
        if (savedIndex !== null) {
            currentPuzzleIndex = parseInt(savedIndex);
        }

        // Show puzzle and update controls
        showPuzzle();
        updateControls();
    } catch (error) {
        console.error('Error loading puzzles:', error);
    }
}

function showPuzzle() {
    if (puzzles.length === 0) return;
    
    const puzzle = puzzles[currentPuzzleIndex];
    const frame = document.getElementById('puzzle-frame');
    
    if (puzzle.analysis_url) {
        frame.src = puzzle.analysis_url;
    }

    // Update puzzle counter
    document.getElementById('puzzle-counter').textContent = 
        `${currentPuzzleIndex + 1} of ${puzzles.length}`;
        
    // Save current position to localStorage using pack-specific key
    localStorage.setItem(storageKey, currentPuzzleIndex);
}

function updateControls() {
    document.getElementById('prevButton').disabled = currentPuzzleIndex === 0;
    document.getElementById('nextButton').disabled = currentPuzzleIndex === puzzles.length - 1;
}

function nextPuzzle() {
    if (currentPuzzleIndex < puzzles.length - 1) {
        currentPuzzleIndex++;
        showPuzzle();
        updateControls();
    }
}

function previousPuzzle() {
    if (currentPuzzleIndex > 0) {
        currentPuzzleIndex--;
        showPuzzle();
        updateControls();
    }
}

// Add keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'n') {
        nextPuzzle();
    } else if (e.key === 'ArrowLeft' || e.key === 'p') {
        previousPuzzle();
    }
});

// Load puzzles when page loads
loadPuzzles(); 