import lxml.etree as ET

class AssignmentXmlToJson():    
    fields = (
        "id",
        "lastUpdateDate",
        "purgeIndicator",
        "recordedDate",
        "pageCount",
        "conveyanceText",
        "assignmentRecordHasImages",
        "attorneyDockNum",
        "corrName",
        "corrAddress1",
        "corrAddress2",
        # Properties
        'inventionTitle', 
        'inventors', 
        'applNum', 
        'filingDate', 
        'publNum', 
        'publDate', 
        'patNum', 
        'issueDate', 
        'pctNum', 
        'intlRegNum',
        # Assignors
        'patAssignorName', 
        'patAssignorExDate', 
        'patAssignorDateAck',
        # Assignees
        'patAssigneeName', 
        'patAssigneeAddress1', 
        'patAssigneeAddress2', 
        'patAssigneeCity', 
        'patAssigneeState', 
        'patAssigneeCountryName', 
        'patAssigneePostcode'
    )
    
    def iterparse(self, file_obj):
        for _, element in ET.iterparse(file_obj, tag="doc"):
            doc = self.convert_doc(element)
            doc['properties'] = self.zip_fields(doc, ('inventionTitle', 'inventors', 'applNum', 'filingDate', 'publNum', 'publDate', 'patNum', 'issueDate', 'pctNum', 'intlRegNum', ))
            doc['assignees'] = self.zip_fields(doc, ('patAssigneeName', 'patAssigneeAddress1', 'patAssigneeAddress2', 'patAssigneeCity', 'patAssigneeState', 'patAssigneeCountryName', 'patAssigneePostcode'))
            doc['assignors'] = self.zip_fields(doc, ('patAssignorName', 'patAssignorExDate', 'patAssignorDateAck'))
            yield doc

    def get_value(self, el):
        value = el.text
        return None if value == "NULL" else value
    
    def convert_doc(self, el):
        doc = dict()
        for e in el:
            key = e.attrib['name']
            if key not in self.fields:
                continue
            if e.tag == "arr":
                doc[key] = [self.get_value(i) for i in e]
            else:
                doc[key] = self.get_value(e)
        return doc

    def zip_fields(self, doc, fields):
        keys = fields
        values = [doc[f] for f in fields]
        for f in fields:
            del doc[f]
        return [dict(zip(keys, v)) for v in zip(*values)]
    