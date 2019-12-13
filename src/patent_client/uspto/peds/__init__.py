from .manager import USApplicationManager
from .model import USApplication

USApplication.objects = USApplicationManager()