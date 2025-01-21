import json


def parse_stringified_object(value):
    """This function assumes that you're dealing with a nested
    stringified object. In the frontend, the entire object should
    be stringified aswell as nested structures."""

    return json.loads(value[0])
