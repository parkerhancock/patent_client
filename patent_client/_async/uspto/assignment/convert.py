import lxml.etree as ET


def convert_doc(doc):
    output = dict()
    for e in doc.iterchildren():
        if e.tag in ("str", "date", "int"):
            output[e.attrib["name"]] = None if e.text == "NULL" else e.text
        elif e.tag == "arr":
            output[e.attrib["name"]] = [
                None if c.text == "NULL" else c.text for c in e.iterchildren()
            ]
    # Collect assignors into a list of dicts
    assignor_fields = ["patAssignorName", "patAssignorExDate", "patAssignorDateAck"]
    output["assignors"] = zip_lists(output, assignor_fields, "assignor")
    # Collect assignees into a list of dicts
    assignee_fields = [
        "patAssigneeName",
        "patAssigneeAddress1",
        "patAssigneeAddress2",
        "patAssigneeCity",
        "patAssigneeState",
        "patAssigneePostcode",
        "patAssigneeCountryName",
    ]
    output["assignees"] = zip_lists(output, assignee_fields, "assignee")
    # Collect properties into a list of dicts
    property_fields = [
        "inventionTitle",
        "inventionTitleLang",
        "applNum",
        "filingDate",
        "intlPublDate",
        "intlRegNum",
        "inventors",
        "issueDate",
        "patNum",
        "pctNum",
        "publDate",
        "publNum",
    ]
    output["properties"] = zip_lists(output, property_fields, "property")
    # Delete the original fields
    for key in assignor_fields + assignee_fields + property_fields:
        del output[key]
    # Collect the correspondent into a dict
    corr_address_fields = ["corrAddress1", "corrAddress2", "corrAddress3"]
    correspondent_address = "\n".join(output[k] for k in corr_address_fields if k in output)
    if correspondent_address:
        output["corr_address"] = correspondent_address
    for key in corr_address_fields:
        if key in output:
            del output[key]
    output["correspondent"] = {
        "name": output["corrName"],
        "address": output["corr_address"],
    }
    del output["corrName"]
    del output["corr_address"]

    # Collect the address for each assignee into a single string
    for assignee in output["assignees"]:
        address_lines = "\n".join(
            assignee[k] for k in ["patAssigneeAddress1", "patAssigneeAddress2"] if assignee[k]
        )
        last_line = f"{assignee['patAssigneeCity']}, {assignee['patAssigneeState']} {assignee['patAssigneePostcode']}"
        if assignee["patAssigneeCountryName"]:
            last_line += f" ({assignee['patAssigneeCountryName']})"
        assignee_address = "\n".join([address_lines, last_line])
        if assignee_address:
            assignee["patAssigneeAddress"] = assignee_address
        for key in [
            "patAssigneeAddress1",
            "patAssigneeAddress2",
            "patAssigneeCity",
            "patAssigneeState",
            "patAssigneePostcode",
            "patAssigneeCountryName",
        ]:
            del assignee[key]

    return output


def zip_lists(data, input_keys, output_key):
    """Zip lists of data into a list of dicts"""
    tuples = list(zip(*[data[key] for key in input_keys]))
    dicts = [dict(zip(input_keys, t)) for t in tuples]
    return dicts


def convert_xml_to_json(xml_text) -> dict:
    """Convert the idiosyncratic xml of the Assignment API to ordinary json"""
    tree = ET.fromstring(xml_text)
    output = dict()
    num_found = tree.find(".//result")
    output["numFound"] = num_found.attrib["numFound"] if num_found is not None else 0
    output["docs"] = [convert_doc(doc) for doc in tree.findall(".//result/doc")]
    return output
