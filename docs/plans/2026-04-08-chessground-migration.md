# Chessground Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace broken Lichess iframe with client-side chessground + chess.js board for interactive puzzle display.

**Architecture:** Use chessground (Lichess's board UI) loaded via CDN ESM modules for rendering, paired with chess.js for legal move validation. Board auto-orients based on side to move in the FEN. An "Analyze on Lichess" link opens the current position.

**Tech Stack:** chessground (CDN), chess.js (CDN), vanilla JS ES modules

---

### Task 1: Update pack_template.html

**Files:**
- Modify: `docs/pack_template.html`

**Step 1: Replace iframe with board div and add CDN imports**

Replace the iframe element and script tags with:
- Chessground CSS (base, brown theme, cburnett pieces) via jsdelivr CDN
- A `<div id="board">` container instead of the iframe
- An "Analyze on Lichess" link below controls
- ES module script imports for chessground and chess.js

```html
<!DOCTYPE html>
<html>
<head>
    <title>2D Tactics - {PACK_NAME}</title>
    <meta name="viewport" content="width=device-width">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@lichess-org/chessground/assets/chessground.base.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@lichess-org/chessground/assets/chessground.brown.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@lichess-org/chessground/assets/chessground.cburnett.css">
</head>
<body>
    <div class="container">
        <div class="nav-header">
            <a href="../index.html" class="back-button" title="Back to Packs">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M19 12H5M12 19l-7-7 7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </a>
        </div>
        <h2 class="pack-title">{PACK_NAME}</h2>
        <div id="board-container">
            <div id="board"></div>
        </div>
        <div class="controls">
            <button class="button" id="prevButton" onclick="previousPuzzle()">Previous</button>
            <div id="puzzle-counter">1 of 50</div>
            <button class="button" id="nextButton" onclick="nextPuzzle()">Next</button>
        </div>
        <a id="analyze-link" class="button analyze-button" target="_blank" rel="noopener">Analyze on Lichess</a>
    </div>
    <script>
        const PUZZLE_PACK = '{PUZZLE_FILE}';
    </script>
    <script type="module" src="../script.js"></script>
</body>
</html>
```

**Step 2: Verify by opening a pack page in browser**

Expected: Page loads without errors, board div visible (empty), controls visible, Lichess link visible.

---

### Task 2: Rewrite script.js with chessground + chess.js

**Files:**
- Modify: `docs/script.js`

**Step 1: Rewrite script.js**

The new script.js:
- Imports Chessground and Chess from CDN ESM
- Loads puzzle CSV as before
- Creates a chessground instance in the `#board` div
- Uses chess.js to compute legal moves (`toDests` helper)
- Auto-orients board based on FEN side to move
- Updates "Analyze on Lichess" link with current position FEN
- Handles prev/next/keyboard navigation

Key functions:
- `toDests(chess)` — converts chess.js legal moves to chessground Map format
- `setupBoard(fen)` — initializes/reconfigures chessground + chess.js for a FEN
- `onMove(orig, dest)` — handles user move: update chess.js, recalculate dests, update link
- `showPuzzle()` — loads puzzle FEN and calls setupBoard
- `updateAnalysisLink()` — updates the Lichess analysis URL from current chess.js FEN

**Step 2: Test in browser**

Expected: Board renders with pieces, can drag/make legal moves, prev/next works, Lichess link opens correct position.

---

### Task 3: Update styles.css for board layout

**Files:**
- Modify: `docs/styles.css`

**Step 1: Replace iframe styles with board styles**

- Remove `#puzzle-frame` styles
- Add `#board-container` with max-width and centering
- Add `#board` with `aspect-ratio: 1` for square board
- Add `.analyze-button` styles
- Ensure responsive sizing

**Step 2: Test responsiveness in browser**

Expected: Board is square, centered, scales on mobile, dark theme consistent.

---

### Task 4: Regenerate pack pages from template

**Files:**
- Modify: `docs/packs/random.html`
- Modify: `docs/packs/opening.html`
- Modify: `docs/packs/middlegame.html`
- Modify: `docs/packs/endgame.html`

**Step 1: Run generate_pack_pages.js**

```bash
cd docs && node generate_pack_pages.js
```

**Step 2: Verify all 4 pack pages are updated**

Expected: Each pack page has the new board div structure instead of iframe.

---

### Task 5: Commit

```bash
git add docs/
git commit -m "Replace Lichess iframe with chessground + chess.js board"
```
