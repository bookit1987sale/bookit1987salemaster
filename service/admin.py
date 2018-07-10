from __future__ import unicode_literals

from django.contrib import admin

from .models import (Branch, Service)#, PartsForService)


admin.site.register(Branch)
# admin.site.register(Base)
admin.site.register(Service)
# admin.site.register(PartsForService)
