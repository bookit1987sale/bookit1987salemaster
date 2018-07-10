import datetime
import json
import time

# from datetime import datetime
from datetime import timedelta
from operator import itemgetter

from source_utils.settings import STAFF_TITLE
from django.shortcuts import render

from django.utils.timezone import localtime, localdate
from django.utils import timezone
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404

from django.contrib.auth.models import User
from rest_framework import generics, permissions, renderers, viewsets, mixins
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from account.models import Account
from service.models import Service, Branch
from consortium.models import Company, Hours, Holidays
from staffer.models import StaffMember
from consumer.models import ClientMember
from source_utils.time_selector import (
    DAYS_OF_WEEK,
    order_weekdays,
    day_plus_12_time_to_datetime
    )
from source_utils.time_selector import order_weekdays

from source_utils.re_usables import (
    add_minutes,
    sub_minutes,
    appt_time_conversion
    )
from event.models import (
    ClientEvent,
    StaffEvent,
    SecondPartEvent,
    # AvailabilityForDay
    )
from staff_sced.models import AvailabilityForDay
from staff_sced.forms import (
    StaffHoursCreateForm,
    StaffHoursUpdateForm,
    company_details
    )
# from snippets.permissions import IsOwnerOrReadOnly
from event.serializers import ClientEventSerializer, GetAvailDateSerializer

from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
    )
from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


class AvailabilityList(ListView):
    model = AvailabilityForDay
    template_name = "staff/staff_avail_list.html"
    context_object_name = 'staff_avail'

    def get_queryset(self):
        staff_avail = AvailabilityForDay.objects.filter(
            staff_member__slug=self.kwargs['slug']
            )
        days_still_avail = False
        days_accounted = []
        for day in staff_avail:
            days_accounted.append(day.day)
        days_open = Hours.objects.filter(
            closed=False
            )
        for day in days_open:
            if day.day not in days_accounted:
                days_still_avail = True
        self.avail = days_still_avail
        return order_weekdays(staff_avail)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = get_object_or_404(
            StaffMember, slug=self.kwargs['slug']
            )
        context['avail'] = self.avail
        return context


class MyAvailCreate(CreateView):
    model = AvailabilityForDay
    success_message = "%(item)s was successfully created"
    template_name = "form.html"
    success_url = reverse_lazy('staff:all_staff')
    form_class = StaffHoursCreateForm

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_initial(self):
        # print(self.kwargs.get('pk'), " self.pk")
        staff_days = AvailabilityForDay.objects.filter(
            staff_member__pk=self.kwargs.get('pk')
            )
        day_hours = Hours.objects.all()
        closed_list = []
        for day in day_hours:
            if day.closed:
                closed_list.append(day.day)
        used_days = []
        for day in staff_days:
            used_days.append(day.day)
        self.unused_day = ""
        for week_day in DAYS_OF_WEEK:
            if week_day[0] not in used_days and week_day[0] not in closed_list:
                self.unused_day = week_day[0]
                break
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs.get('pk'))
        print(self.staff, " self.pk ",self.unused_day)
        # start, end, step = company_details(self.unused_day)
        hours = Hours.objects.get(day=self.unused_day)
        print(hours.start, hours.end)
        return {
            'staff_member': self.staff,
            'day': self.unused_day,
            'scheduled_start':hours.start,
            'scheduled_end':hours.end,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add to {}'s Availability for {}".format(
            self.staff.get_friendly_name(),
            self.unused_day
            )
        context['button'] = "Add"
        context['company'] = get_object_or_404(Company, pk=1)
        return context


class MyAvailUpdate(UpdateView):
    model = AvailabilityForDay
    success_message = "%(item)s was successfully updated"
    template_name = "form.html"
    success_url = reverse_lazy('staff:all_staff')
    form_class = StaffHoursUpdateForm
    
    def get_initial(self):
        # print(self.object.day)
        return {
            'day': self.object.day
        }

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update {}'s Availability for {}".format(
            self.object.staff_member.get_friendly_name(),
            self.object.day
            )
        context['button'] = "Update"
        context['company'] = get_object_or_404(Company, pk=1)
        return context
