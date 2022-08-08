import re
from dataclasses import dataclass
from pathlib import Path

base_dir = Path(__file__).parent


@dataclass
class NumberServiceError:
    code: str
    message: str
    kind: str = "MESSAGE"

    def __str__(self):
        return f"{self.code} -- {self.message}"


def build_error_dir():
    error_re = re.compile(r"(?P<code>pBRE\d{3,}) (?P<message>.*) (?P<kind>WARNING|ERROR)$")
    error_text = (base_dir / "errors.txt").read_text()
    errors = [NumberServiceError(**error_re.search(l).groupdict()) for l in error_text.split("\n")]
    message_text = (base_dir / "messages.txt").read_text()
    message_re = re.compile(r"(?P<code>BR(E|W)\d{3,}) (?P<message>.*)$")
    messages = [NumberServiceError(**message_re.search(l).groupdict()) for l in message_text.split("\n")]
    errors = {e.code: e for e in errors + messages}
    errors["SUCCESS"] = None
    return errors
