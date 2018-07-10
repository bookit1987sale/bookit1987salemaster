from django.contrib import admin

from .models import (
	ClientEvent,
	StaffEvent,
	# AvailabilityForDay,
	StaffActivityType,
	SecondPartEvent
	)

admin.site.register(ClientEvent)
admin.site.register(StaffEvent)
# admin.site.register(AvailabilityForDay)
admin.site.register(StaffActivityType)
admin.site.register(SecondPartEvent)