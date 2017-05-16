from django.contrib import admin

from .models import Badge, AwardDef, Award

admin.site.register(Award)
admin.site.register(Badge)