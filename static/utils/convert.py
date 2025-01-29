import json
from static.utils.logging import log_debug


def parse_stringified_object(value):
    """This function assumes that you're dealing with a nested
    stringified object. In the frontend, the entire object should
    be stringified aswell as nested structures."""

    return json.loads(value[0])


def convert_str_to_complex_obj(show_debugging, data, entries):
    """
    Convert specified fields in a dictionary from JSON strings to
    complex objects (e.g., lists or dictionaries) that Python can
    handle natively.

    Parameters:
        show_debugging (bool): Show debugging logs if true.
        data (dict): The dictionary containing fields to process.
        entries (list): A list of keys in `data` whose values should be
        converted.

    Returns: None
    """
    for i in entries:
        if i in data:
            previous_type = type(data[i])
            # Convert variable to complex object
            data[i] = json.loads(data[i])
            converted_type = type(data[i])
            log_debug(
                show_debugging,
                f"Converted data entry ({i}) from {previous_type} to "
                + str(converted_type),
                data[i],
            )
