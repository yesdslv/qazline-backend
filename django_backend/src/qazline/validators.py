import jsonschema
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator

ANSWER_JSON_FIELD_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'answer_text': {
                'type': 'string',
            },
            'correct': {
                'type': 'boolean',
            },
        },
        'required': ['answer_text'],
        'additionalProperties': False,
    },
    "minItems": 1,
    "maxItems": 10,
}


class JSONSchemaValidator(BaseValidator):
    def compare(self, value, schema):
        try:
            jsonschema.validate(value, schema)
        except jsonschema.exceptions.ValidationError:
            raise ValidationError({'answers': f'{value} failed JSON schema check'})
