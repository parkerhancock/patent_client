from .model import Inpadoc, InpadocBiblio
from .manager import InpadocManager

Inpadoc.objects = InpadocManager()

InpadocBiblio.objects = InpadocManager().set_options(constituent='biblio')