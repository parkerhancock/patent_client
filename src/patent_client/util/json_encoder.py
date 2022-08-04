import datetime
import json


class JsonEncoder(json.JSONEncoder):
    def default(self, o: "Any") -> "Any":
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        elif hasattr(o, "to_dict"):
            return o.to_dict()
        return json.JSONEncoder.default(self, o)
