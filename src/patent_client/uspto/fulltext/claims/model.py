from attr import attrs, attrib, Factory
import textwrap

@attrs(auto_attribs=True, repr=False)
class Claim(object):
    number: int
    #text: str
    limitations: "List[str]"
    depends_on: "Optional[int]"
    depends_on_claim: "Optional[int]" = attrib(default=None)
    dependent_claims: "List[Claim]" = Factory(list)
    
    def __repr__(self):
        return f"Claim(number={self.number}, depends_on={self.depends_on}, text={textwrap.shorten(self.text, width=40, placeholder='...')})"

    @property
    def text(self):
        return  f"{self.number}. " + "\n".join(self.limitations)

    @property
    def independent(self):
        return self.depends_on is None
    
    @property
    def dependent(self):
        return self.depends_on is not None