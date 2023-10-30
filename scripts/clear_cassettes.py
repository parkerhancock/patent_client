from pathlib import Path


def clear_cassettes():
    cassettes = list(Path(__file__).parent.parent.glob("**/cassettes/**/*.yaml"))
    for cassette in cassettes:
        print(cassette)
        cassette.unlink()


if __name__ == "__main__":
    clear_cassettes()
