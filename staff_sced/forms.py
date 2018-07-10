import string

import datetime
from datetime import timedelta

from django import forms
from django.utils import timezone
from bootstrap_datepicker.widgets import DatePicker
from consortium.models import Company
from consumer.models import ClientMember
from staff_sced.models import AvailabilityForDay
from source_utils.form_mixins import (
    check_name, 
    check_phone_options, 
    company_name_check
)
from consortium.models import Hours, Holidays
from source_utils.time_selector import select_time_options
from source_utils.re_usables import time_format_no_zero, add_minutes


def match_company_hours(check_day, check_start, check_end):
    company_day_hours = Hours.objects.all()
    problems = {}
    for day in company_day_hours:
        if check_day == day:
            if day.start > check_start:
                problems['start'] = day.start
            if day.end < check_end:
                problems['end'] = day.end
        continue
    return problems


def company_details(day):
    company = Company.objects.get(pk=1)
    time_step = company.work_step
    hours = Hours.objects.get(day=day)
    return {
        'start':hours.start,
        'end':hours.end,
        'step':time_step
        }


class StaffHoursUpdateForm(forms.ModelForm):
    class Meta:
        model = AvailabilityForDay
        fields = (
            'scheduled_start',
            'scheduled_end',
            'not_avail'
            )
    
    def __init__(self, *args, **kwargs):
        super(StaffHoursUpdateForm, self).__init__(*args, **kwargs)
        # print(dir(self.fields['scheduled_start']), " llkkk")
        # print(kwargs['initial']['day'], " llk8888kk")
        self.fields['scheduled_start'].widget = forms.Select(
            choices=select_time_options(
                company = company_details(kwargs['initial']['day']), option=1
            )
        )
        self.fields['scheduled_end'].widget = forms.Select(
            choices=select_time_options(
                company=company_details(kwargs['initial']['day'])
            )
        )

    def clean(self):
        if self.cleaned_data["not_avail"] == False:
            if self.cleaned_data["scheduled_start"] and self.cleaned_data["scheduled_end"]:
                if datetime.datetime.strptime(
                    self.cleaned_data["scheduled_start"],
                    "%I:%M %p") >= datetime.datetime.strptime(
                            self.cleaned_data["scheduled_end"],
                                "%I:%M %p"
                                ):
                    raise forms.ValidationError("End time must exeed start time.")
            else:
                if not self.cleaned_data["scheduled_start"] or not self.cleaned_data["scheduled_end"]:
                    raise forms.ValidationError("If staff is available for day, valid start and end times are required.")
        return self.cleaned_data


class StaffHoursCreateForm(forms.ModelForm):

    class Meta:
        model = AvailabilityForDay
        fields = (
            'staff_member',
            'day',
            'scheduled_start',
            'scheduled_end',
            'not_avail'
            )
        widgets = {'staff_member': forms.HiddenInput(),
                   'day': forms.HiddenInput()}
        # form = MyForm(initial={'max_number': '3'})

    def __init__(self, *args, **kwargs):
        super(StaffHoursCreateForm, self).__init__(*args, **kwargs)

        self.fields['scheduled_start'].widget = forms.Select(
            choices=select_time_options(
                company = company_details(kwargs['initial']['day']), option=1
            )
        )
        self.fields['scheduled_end'].widget = forms.Select(
            choices=select_time_options(
                company=company_details(kwargs['initial']['day'])
            )
        )

    def clean(self):
        if self.cleaned_data["not_avail"] == False:
            if self.cleaned_data["scheduled_start"] and self.cleaned_data["scheduled_end"]:
                if datetime.datetime.strptime(
                    self.cleaned_data["scheduled_start"],
                    "%I:%M %p") >= datetime.datetime.strptime(
                            self.cleaned_data["scheduled_end"],
                                "%I:%M %p"
                                ):
                    raise forms.ValidationError("End time must exeed start time.")
            else:
                if not self.cleaned_data["scheduled_start"] or not self.cleaned_data["scheduled_end"]:
                    raise forms.ValidationError("If staff is available for day, valid start and end times are required.")
        return self.cleaned_data
