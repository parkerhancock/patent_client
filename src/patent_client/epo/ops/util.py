from patent_client.util.xml import Schema as XmlSchema

class Schema(XmlSchema):
    class Meta:
        namespaces = {
        "ops": "http://ops.epo.org",
        "epo": "http://www.epo.org/exchange",
        "ft": "http://www.epo.org/fulltext",
    }