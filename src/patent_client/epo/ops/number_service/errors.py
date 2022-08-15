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


error_re = re.compile(r"(?P<code>pBRE\d{3,}) (?P<message>.*) (?P<kind>WARNING|ERROR)$")
message_re = re.compile(r"(?P<code>BR(E|W)\d{3,}) (?P<message>.*)$")


def get_errors(string):
    match = error_re.search(string)
    return match.groupdict() if match else None


def get_messages(string):
    match = message_re.search(string)
    return match.groupdict() if match else None


def build_error_dir():

    error_text = (base_dir / "errors.txt").read_text()
    errors = [get_errors(err) for err in error_text.split("\n")]
    message_text = (base_dir / "messages.txt").read_text()
    messages = [get_messages(err) for err in message_text.split("\n")]
    error_objs = [NumberServiceError(**e) for e in errors + messages if e]
    errors = {e.code: e for e in error_objs if e}
    errors["SUCCESS"] = None
    return errors
