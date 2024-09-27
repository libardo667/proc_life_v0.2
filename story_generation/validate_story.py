import json
import jsonschema
from jsonschema import validate
import jsonschema.exceptions

def validate_json(data, json_schema):
    try:
        validate(instance=data, schema=json_schema)
        return True, None
    except jsonschema.exceptions.ValidationError as err:
        return False, err