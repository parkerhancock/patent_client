from pathlib import Path

import hishel
from patent_client.util.request_util import SimpleController

cert = str(Path(__file__).parent / "developer.uspto.gov.crt")

session = hishel.AsyncCacheClient(controller=SimpleController(max_age=3 * 24 * 60 * 60), verify=cert)
