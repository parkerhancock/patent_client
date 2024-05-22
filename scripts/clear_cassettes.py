from pathlib import Path

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent
    for cassette_file in base_path.glob("**/cassettes/**/*.yaml"):
        cassette_file.unlink()
