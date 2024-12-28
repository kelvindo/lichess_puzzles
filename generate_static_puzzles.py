from generate_puzzles import PuzzleGenerator, PUZZLES_RANDOM
import os
import csv
import argparse
import random
def generate_static_puzzles(num_puzzles: int, puzzle_pack: str, 
                          start_elo: int, end_elo: int) -> list:
    """Generate a static dataset of puzzles with ELO ratings between start_elo and end_elo.
    
    Args:
        num_puzzles: Number of puzzles to generate
        puzzle_pack: The puzzle pack to use
        start_elo: Starting ELO rating (inclusive)
        end_elo: Ending ELO rating (inclusive)
    """
    puzzle_generator = PuzzleGenerator()
    puzzles = []

    # Divide num_puzzles by 2 since we are generating both offensive and defensive puzzles
    num_puzzles = num_puzzles // 2
    for i in range(num_puzzles):
        # Calculate ELO for this puzzle - linear distribution between start and end
        elo = start_elo + (end_elo - start_elo) * (i / (num_puzzles - 1)) if num_puzzles > 1 else start_elo
        elo = int(round(elo))
        
        # Get both offensive and defensive puzzles
        (offensive_fen, offensive_url), (defensive_fen, defensive_url) = (
            puzzle_generator.generate_puzzle_fen_strings(
                puzzle_pack,
                elo,
                None,
                None
            )
        )
        
        # Add both puzzles to the list
        puzzles.extend([
            {
                'fen': offensive_fen,
                'analysis_url': offensive_url,
                'elo': elo,
                'type': 'offensive'
            },
            {
                'fen': defensive_fen,
                'analysis_url': defensive_url,
                'elo': elo,
                'type': 'defensive'
            }
        ])

    # Shuffle the puzzles
    random.shuffle(puzzles)
    
    return puzzles

def export_puzzles_to_csv(output_dir: str, num_puzzles: int,
                         puzzle_pack: str, start_elo: int, 
                         end_elo: int):
    """Generate puzzles and save them as a CSV file with metadata in the filename.
    
    Args:
        output_dir: Output directory for the CSV file
        num_puzzles: Number of puzzles to generate
        puzzle_pack: The puzzle pack to use
        start_elo: Starting ELO rating
        end_elo: Ending ELO rating
    """
    
    # Generate puzzles
    puzzles = generate_static_puzzles(num_puzzles, puzzle_pack, start_elo, end_elo)
    
    if puzzles:
        # Create filename with metadata
        filename = f"puzzles_{puzzle_pack}_n{num_puzzles}_elo{start_elo}-{end_elo}.csv"
        filepath = os.path.join(output_dir, filename)
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            if puzzles and len(puzzles) > 0:
                writer.writerow(puzzles[0].keys())
                for puzzle in puzzles:
                    writer.writerow(puzzle.values())
        print(f"Saved {len(puzzles)} puzzles to {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate static chess puzzles')
    parser.add_argument('--num_puzzles', type=int, default=100,
                      help='Number of puzzles to generate')
    parser.add_argument('--puzzle_pack', type=str, default=PUZZLES_RANDOM,
                      help='Puzzle pack to use')
    parser.add_argument('--start_elo', type=int, default=1000,
                      help='Starting ELO rating')
    parser.add_argument('--end_elo', type=int, default=1000,
                      help='Ending ELO rating')
    parser.add_argument('--output_dir', type=str, default="docs/static_puzzles",
                      help='Output directory for the CSV file')
    
    args = parser.parse_args()
    
    # Export puzzles using the export function
    export_puzzles_to_csv(
        output_dir=args.output_dir,
        num_puzzles=args.num_puzzles,
        puzzle_pack=args.puzzle_pack,
        start_elo=args.start_elo,
        end_elo=args.end_elo
    ) 