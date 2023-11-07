# -*- coding: utf-8 -*-
"""

@author: chris
"""
from patent_client.epo.ops.register.api import EPRegisterSearchApi
from patent_client.epo.ops.register.model import EPRegister
from patent_client.epo.ops.register.model import Inpadoc
from patent_client.epo.ops.register.manager import EPRegisterSearchManager


# EPRegisterSearchApi()
print("-------------------- API TEST --------------------")
print()
test_API = EPRegisterSearchApi()
search_result = test_API.search("EP1000000")
print(search_result)
print(len(str(search_result)))
print()

# model
print("-------------------- MODEL TEST --------------------")
print()
test_model = EPRegister.objects.get("EP1000000")
#print(test_model)
print("Agent: " + test_model.agent)
print("Applicant: " + test_model.applicant)
print()

