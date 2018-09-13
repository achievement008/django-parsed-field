from django.contrib import admin
from .models import ParseFieldsRules


class ParseFieldsRulesAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ParseFieldsRules._meta.fields]

    class Meta:
        model = ParseFieldsRules


admin.site.register(ParseFieldsRules, ParseFieldsRulesAdmin)
