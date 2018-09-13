from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from ._make_rules import RulesDictCreator
from parsedfield.models import ParseFieldsRules


class Command(BaseCommand):
    help = 'Create dict of rules for given json-parsed-field'

    def add_arguments(self, parser):
        parser.add_argument('parsefield', nargs='+', type=str)

    def handle(self, *args, **options):
        for field in options['parsefield']:
            try:
                model = ContentType.objects.get(model=field.split('.')[0].lower())
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.ERROR('Model "%s" not found' % field.split('.')[0]))
            else:
                if field.split('.')[-1] not in [i.name for i in model.model_class()._meta.fields]:
                    self.stdout.write(self.style.ERROR('Field "%s" not found in model fields' % field.split('.')[-1]))
                elif model.model_class()._meta.get_field(field.split('.')[-1]).__class__.__name__ != 'JSONParsedField':
                    self.stdout.write(self.style.ERROR('Field "%s" must be type of JSONParsedField' % field.split('.')[-1]))
                else:
                    rules_creater = RulesDictCreator()
                    rules_creater.start()
                    if rules_creater.rules:
                        ParseFieldsRules.objects.create(
                            model=field.split('.')[0].lower(),
                            field=field.split('.')[-1],
                            rules=rules_creater.rules
                        )
                        self.stdout.write(self.style.SUCCESS('Successfully created rules for field "%s"' % field))
                    else:
                        self.stdout.write(self.style.ERROR('Rules for field "%s" was not created' % field))
