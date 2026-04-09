import { Chessground } from 'https://cdn.jsdelivr.net/npm/@lichess-org/chessground/+esm';
import { Chess } from 'https://cdn.jsdelivr.net/npm/chess.js@1.0.0/+esm';

let puzzles = [];
let currentPuzzleIndex = 0;
let ground = null;
let chess = null;
let currentPuzzleFen = null;
let moveHistory = [];
let moveIndex = -1;
const storageKey = `currentPuzzleIndex_${PUZZLE_PACK}`;

function toDests(chess) {
    const dests = new Map();
    for (const move of chess.moves({ verbose: true })) {
        if (!dests.has(move.from)) {
            dests.set(move.from, []);
        }
        dests.get(move.from).push(move.to);
    }
    return dests;
}

function toColor(chess) {
    return chess.turn() === 'w' ? 'white' : 'black';
}

function updateAnalysisLink() {
    const link = document.getElementById('analyze-link');
    if (chess) {
        const fen = chess.fen().replace(/ /g, '_');
        link.href = `https://lichess.org/analysis/${fen}`;
    }
}

function setupBoard(fen) {
    currentPuzzleFen = fen;
    moveHistory = [];
    moveIndex = -1;
    chess = new Chess(fen);
    const orientation = chess.turn() === 'b' ? 'black' : 'white';

    const config = {
        fen: fen,
        orientation: orientation,
        turnColor: toColor(chess),
        movable: {
            color: 'both',
            free: false,
            dests: toDests(chess),
        },
        events: {
            move: onMove,
        },
    };

    if (ground) {
        ground.set(config);
    } else {
        ground = Chessground(document.getElementById('board'), config);
    }

    updateAnalysisLink();
}

function onMove(orig, dest) {
    chess.move({ from: orig, to: dest, promotion: 'q' });
    // Truncate any forward history when a new move is made
    moveHistory = moveHistory.slice(0, moveIndex + 1);
    moveHistory.push(chess.fen());
    moveIndex++;
    syncBoard();
}

function syncBoard() {
    ground.set({
        fen: chess.fen(),
        turnColor: toColor(chess),
        movable: {
            color: 'both',
            dests: toDests(chess),
        },
    });
    updateAnalysisLink();
}

function undoMove() {
    if (moveIndex >= 0) {
        moveIndex--;
        const fen = moveIndex >= 0 ? moveHistory[moveIndex] : currentPuzzleFen;
        chess = new Chess(fen);
        syncBoard();
    }
}

function redoMove() {
    if (moveIndex < moveHistory.length - 1) {
        moveIndex++;
        chess = new Chess(moveHistory[moveIndex]);
        syncBoard();
    }
}

function resetPosition() {
    if (currentPuzzleFen) {
        moveHistory = [];
        moveIndex = -1;
        chess = new Chess(currentPuzzleFen);
        syncBoard();
    }
}

async function loadPuzzles() {
    try {
        const response = await fetch(`../static_puzzles/${PUZZLE_PACK}`);
        const csvText = await response.text();

        const lines = csvText.split('\n');
        const headers = lines[0].split(',');

        puzzles = lines.slice(1).filter(line => line.trim()).map(line => {
            const values = line.split(',');
            const puzzle = {};
            headers.forEach((header, index) => {
                puzzle[header.trim()] = values[index]?.trim();
            });
            return puzzle;
        });

        const savedIndex = localStorage.getItem(storageKey);
        if (savedIndex !== null) {
            currentPuzzleIndex = parseInt(savedIndex);
        }

        showPuzzle();
        updateControls();
    } catch (error) {
        console.error('Error loading puzzles:', error);
    }
}

function showPuzzle() {
    if (puzzles.length === 0) return;

    const puzzle = puzzles[currentPuzzleIndex];
    if (puzzle.fen) {
        setupBoard(puzzle.fen);
    }

    document.getElementById('puzzle-counter').textContent =
        `${currentPuzzleIndex + 1} of ${puzzles.length}`;

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

// Expose to global scope for onclick handlers
window.nextPuzzle = nextPuzzle;
window.previousPuzzle = previousPuzzle;
window.resetPosition = resetPosition;

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
        redoMove();
    } else if (e.key === 'ArrowLeft') {
        undoMove();
    } else if (e.key === 'n') {
        nextPuzzle();
    } else if (e.key === 'p') {
        previousPuzzle();
    }
});

loadPuzzles();
