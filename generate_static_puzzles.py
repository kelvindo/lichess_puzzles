from generate_puzzles import PuzzleGenerator, PUZZLES_RANDOM
import os
import csv

def generate_static_puzzles(num_puzzles, elo: int = 1000) -> list:
    """Generate a static dataset of puzzles at 1000 ELO."""
    puzzle_generator = PuzzleGenerator()
    puzzles = []
    
    for _ in range(num_puzzles):
        fen, analysis_url = puzzle_generator.generate_puzzle_fen_string(
            PUZZLES_RANDOM, 
            elo, 
            None, 
            None
        )
        puzzles.append({
            'fen': fen,
            'analysis_url': analysis_url
        })
    
    return puzzles

def export_puzzles_to_csv(output_dir: str = "docs/static_puzzles", num_puzzles: int = 100):
    """Generate puzzles and save them as a single CSV file."""
    
    # Generate puzzles
    puzzles = generate_static_puzzles(num_puzzles)
    
    if puzzles:
        filepath = os.path.join(output_dir, "puzzles.csv")
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            if puzzles and len(puzzles) > 0:
                writer.writerow(puzzles[0].keys())
                # Write puzzle data
                for puzzle in puzzles:
                    writer.writerow(puzzle.values())
        print(f"Saved {len(puzzles)} puzzles to {filepath}")

if __name__ == "__main__":
    export_puzzles_to_csv() 