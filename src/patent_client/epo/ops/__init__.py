from .family.model import Family
from .legal.model import Legal
from .published.model import Images
from .published.model import Inpadoc
from .session import session

__api_name__ = "EPO Open Patent Services"
__all__ = ["Family", "Legal", "Images", "Inpadoc", "session"]
