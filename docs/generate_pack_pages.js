const fs = require('fs');
const path = require('path');

const packs = [
    {
        name: 'Random Tactics',
        file: 'puzzles_Random_n50_elo800-1600.csv'
    },
    {
        name: 'Opening Tactics',
        file: 'puzzles_Opening_n50_elo800-1600.csv'
    },
    {
        name: 'Middlegame Tactics',
        file: 'puzzles_Middlegame_n50_elo800-1600.csv'
    },
    {
        name: 'Endgame Tactics',
        file: 'puzzles_Endgame_n50_elo800-1600.csv'
    }
];

// Read the template
const template = fs.readFileSync(path.join(__dirname, 'pack_template.html'), 'utf8');

// Create packs directory if it doesn't exist
const packsDir = path.join(__dirname, 'packs');
if (!fs.existsSync(packsDir)) {
    fs.mkdirSync(packsDir);
}

// Generate a file for each pack
packs.forEach(pack => {
    const fileName = pack.file.split('_')[1].toLowerCase() + '.html';
    const content = template
        .replace(/{PACK_NAME}/g, pack.name)
        .replace(/{PUZZLE_FILE}/g, pack.file);
    
    fs.writeFileSync(path.join(packsDir, fileName), content);
    console.log(`Generated packs/${fileName}`);
}); 