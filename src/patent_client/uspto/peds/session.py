import hishel
from patent_client.util.request_util import SimpleController

session = hishel.AsyncCacheClient(controller=SimpleController(max_age=3 * 24 * 60 * 60))
