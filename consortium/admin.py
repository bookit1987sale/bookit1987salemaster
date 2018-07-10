from __future__ import unicode_literals

from django.contrib import admin

from .models import (Company, Hours, Holidays)

admin.site.register(Company)
admin.site.register(Hours)
admin.site.register(Holidays)