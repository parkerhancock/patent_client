from .manager import PtabProceedingManager, PtabDocumentManager, PtabDecisionManager
from .model import PtabProceeding, PtabDocument, PtabDecision

PtabProceeding.objects = PtabProceedingManager()
PtabDocument.objects = PtabDocumentManager()
PtabDecision.objects = PtabDecisionManager()