from .model import PatentFileWrapperDataBagItem, BulkDataProductBagItem
from .manager import PatentFileWrapperManager, BulkDataManager


PatentFileWrapper = PatentFileWrapperDataBagItem
PatentFileWrapper.objects = PatentFileWrapperManager()

BulkData = BulkDataProductBagItem
BulkData.objects = BulkDataManager()
