import textwrap
from dataclasses import dataclass, field

from ..model import Model


@dataclass
class Claim(Model):
    __exclude__ = ["depends_on_claim", "dependent_claims"]

    number: int
    # text: str
    limitations: "List[str]"
    depends_on: "Optional[int]"
    depends_on_claim: "Optional[int]" = None
    dependent_claims: "List[Claim]" = field(default_factory=list)

    def __repr__(self):
        return f"Claim(number={self.number}, depends_on={self.depends_on}, text={textwrap.shorten(self.text, width=40, placeholder='...')})"

    @property
    def text(self):
        return f"{self.number}. " + "\n".join(self.limitations)

    @property
    def independent(self):
        return self.depends_on is None

    @property
    def dependent(self):
        return self.depends_on is not None
