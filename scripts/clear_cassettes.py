import sys
import typing as tp
from pathlib import Path


def clear_cassettes(path: tp.Optional[Path] = None) -> None:
    if path is None:
        path = Path(__file__).parent.parent
    for cassette_file in path.glob("**/cassettes/**/*.yaml"):
        cassette_file.unlink()


if __name__ == "__main__":
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    clear_cassettes(input_path)
