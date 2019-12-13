from dataclasses import dataclass # type: ignore

@dataclass # type: ignore
class BaseClass(): # type: ignore
    name: str # type: ignore
    attribute: int # type: ignore

@dataclass # type: ignore
class ChildClass(BaseClass): # type: ignore
    birthdate: str # type: ignore