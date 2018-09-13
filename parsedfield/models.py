from django.db import models

from jsonfield import JSONField


class ParseFieldsRules(models.Model):
    rules = JSONField()
    model = models.CharField(max_length=32)
    field = models.CharField(max_length=32)

    def __str__(self):
        return '{0} {1}'.format(self.model, self.field)
