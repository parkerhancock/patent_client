from .model import ITCInvestigation, ITCDocument, ITCAttachment
from .manager import ITCInvestigationManager, ITCDocumentManager, ITCAttachmentManager

ITCInvestigation.objects = ITCInvestigationManager()
ITCDocument.objects = ITCDocumentManager()
ITCAttachment.objects = ITCAttachmentManager()