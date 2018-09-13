import json

from jsonfield.fields import JSONField

from parsedfield.models import ParseFieldsRules
from ._parse_rules import RulesParser


class JSONParsedField(JSONField):
    description = "Field for save parsed json object"

    def __init__(self, *args, **kwargs):
        super(JSONParsedField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if self.null and value is None:
            return None
        rule_objects = ParseFieldsRules.objects.filter(model=self.model.__name__.lower(), field=self.name)
        if rule_objects.exists():
            for rule_object in rule_objects:
                try:
                    parser = RulesParser(rule_object.rules, value)
                    parser.parse()
                except Exception:
                    pass
                else:
                    return json.dumps(parser.searched, **self.dump_kwargs)
        return json.dumps(value, **self.dump_kwargs)
