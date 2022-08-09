import textwrap
from dataclasses import dataclass
from dataclasses import field
from typing import *

from ..base.model import Model


@dataclass
class Claim(Model):
    __exclude__ = ["depends_on_claim", "dependent_claims"]

    number: int
    # text: str
    limitations: "List[str]"
    depends_on: "List[int]" = field(default_factory=list)
    dependent_claims: "List[int]" = field(default_factory=list)

    def __repr__(self):
        return f"Claim(number={self.number}, depends_on={self.depends_on}, text={textwrap.shorten(self.text, width=40, placeholder='...')})"

    @property
    def text(self):
        return f"{self.number}. " + "\n".join(self.limitations)

    @property
    def independent(self):
        return not bool(self.depends_on)

    @property
    def dependent(self):
        return bool(self.depends_on)
