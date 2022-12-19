from patent_client.epo.ops.register.api import EPRegisterSearchApi
from patent_client.epo.ops.register.model import EPRegister
from patent_client.epo.ops.register.model import Inpadoc
from patent_client.epo.ops.register.manager import EPRegisterSearchManager


def test_register_api():
    test_API = EPRegisterSearchApi()
    search_result = test_API.search("EP1000000")
    print(search_result)
    print(len(str(search_result)))
    breakpoint()

def test_model():
    test_model = EPRegister.objects.get("EP1000000")
    #print(test_model)
    print("Agent: " + test_model.agent)

