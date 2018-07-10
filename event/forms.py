import string

from datetime import datetime
from datetime import timedelta

from django import forms
from django.utils import timezone
from bootstrap_datepicker.widgets import DatePicker
from .models import ClientEvent, StaffEvent
from consortium.models import Company
from consumer.models import ClientMember
# from staff_sced.views import AvailabilityForDay
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


# def company_details(day):
#     company = Company.objects.get(pk=1)
#     time_step = company.work_step
#     hours = Hours.objects.get(day=day)
#     return {
#         'start':hours.start,
#         'end':hours.end,
#         'step':time_step
#         }


# class StaffHoursUpdateForm(forms.ModelForm):
#     class Meta:
#         model = AvailabilityForDay
#         fields = (
#             'day',
#             'scheduled_start',
#             'scheduled_end',
#             )
    
#     def __init__(self, *args, **kwargs):
#         super(StaffHoursUpdateForm, self).__init__(*args, **kwargs)
#         self.fields['scheduled_start'].widget = forms.Select(
#             choices=select_time_options(
#                 company = company_details(kwargs['initial']['day']), option=1
#             )
#         )
#         self.fields['scheduled_end'].widget = forms.Select(
#             choices=select_time_options(
#                 company=company_details(kwargs['initial']['day'])
#             )
#         )

#     def clean(self):
#         if self.cleaned_data["scheduled_start"] >= self.cleaned_data["scheduled_end"]:
#             raise forms.ValidationError("End time must exeed start time.")
#         return self.cleaned_data


# class StaffHoursCreateForm(forms.ModelForm):

#     class Meta:
#         model = AvailabilityForDay
#         fields = (
#             'staff_member',
#             'day',
#             'scheduled_start',
#             'scheduled_end',
#             )
#         widgets = {'staff_member': forms.HiddenInput(),}

#     def __init__(self, *args, **kwargs):
#         super(StaffHoursCreateForm, self).__init__(*args, **kwargs)
#         self.fields['day'].widget = forms.Select(choices=kwargs['initial']['day'])
#         self.fields['scheduled_start'].widget = forms.Select(choices=select_time_options(
#             company = company_details(kwargs['initial']['day'][0][0]), option=1
#             )
#         )
#         all_end_choices = choices=select_time_options(
#             company=company_details(kwargs['initial']['day'][0][0])
#             )
#         self.fields['scheduled_end'].widget = forms.Select(choices=all_end_choices)
#         self.fields['scheduled_end'].initial = all_end_choices[-1]

    # def clean(self):
    #     """
    #     Handles validation and capitilize entries.
    #     """
    #     # problems = match_company_hours(
    #     #     self.cleaned_data["day"],
    #     #     self.cleaned_data["scheduled_start"],
    #     #     self.cleaned_data["scheduled_end"]
    #     #     )
    #     # if problems:
    #     #     if problems.start:
    #     #         error = "On {} we open at {}".format(
    #     #             self.cleaned_data["day"],
    #     #             problems.start
    #     #             )
    #     #         raise forms.ValidationError(error)
    #     #     if problems.end:
    #     #         error = "On {} we close at {}".format(
    #     #             self.cleaned_data["day"],
    #     #             problems.end
    #     #             )
    #     #         raise forms.ValidationError(error)
    #     print(self.cleaned_data["scheduled_start"],
    #         self.cleaned_data["scheduled_end"])
    #     return self.cleaned_data


class ClientEventCreateForm(forms.ModelForm):
    class Meta:
        model = ClientEvent
        fields = (
            "client_service", "staff_client", "user_client", "staff",
            "start"
            )
        widgets = {
            'client_service': forms.HiddenInput(),
            'staff_client': forms.HiddenInput(),
            'user_client': forms.HiddenInput(),
            'staff': forms.HiddenInput(),
            'start': forms.HiddenInput(),
            }


class ClientEventForm(forms.ModelForm):
    class Meta:
        model = ClientEvent
        fields = (
            "client_service", "client_mood", "status"
        )

    def clean(self):
        if self.cleaned_data["client_mood"] != "Not Complete" and self.cleaned_data["status"] == "Not Complete":
            raise forms.ValidationError("'Appointment status' cannot be 'Not Complete' if 'Client's mood' is not.")
        if self.cleaned_data["client_mood"] == "Not Complete" and self.cleaned_data["status"] != "Not Complete":
            raise forms.ValidationError("'Client's mood' cannot be 'Not Complete' if 'Appointment status' is not.")
        return self.cleaned_data


class GetClientForEventForm(forms.ModelForm):
    class Meta:
        model = ClientEvent
        fields = (
            "user_client",
            # "client_service",
        )

    def __init__(self, *args, **kwargs):
        super(GetClientForEventForm, self).__init__(*args, **kwargs)
        self.fields['user_client'].required = True
        # last_appt = ClientEvent.objects.filter(
        #         staff_client=kwargs['client']).latest('start')
        # print(last_appt, " [[[[[[ ", kwargs['client'])
        # self.fields['client_service'].initial = last_appt


class GetTypeOfEventForm(forms.ModelForm):

    class Meta:
        model = ClientEvent
        fields = (
            "client_service",
        )

    def __init__(self, *args, **kwargs):
        super(GetTypeOfEventForm, self).__init__(*args, **kwargs)
        # print(kwargs['initial']['service'])
        # last_appt = ClientEvent.objects.filter(
        #         staff_client=kwargs['client']).latest('start')
        # print(last_appt, " [[[[[[ ", kwargs['client'])
        self.fields['client_service'].initial = kwargs['initial']['service']

    # def get_initial(self):
    #     initial = super(GetTypeOfEvent, self).get_initial()
    #     if self.kwargs.get('ev_type') == 'for_staff':
    #         initial['client_service'] = ClientEvent.objects.filter(
    #             staff_client=self.kwargs.get('client')).latest('start')
    #     else:
    #         initial['client_service'] = ClientEvent.objects.filter(
    #             user_client=self.kwargs.get('client')).latest('start')
    #     return initial


class GetStaffForEventForm(forms.Form):

    staff = forms.CharField()

    class Meta:
        fields = (
            "staff",
        )
    
    def __init__(self, *args, **kwargs):
        super(GetStaffForEventForm, self).__init__(*args, **kwargs)
        self.fields['staff'].widget = forms.Select(choices=kwargs['initial']['poss_staff'])
        self.fields['staff'].required = False


class GetDateForEventForm(forms.Form):

    select_a_date = forms.CharField()

    class Meta:
        fields = (
            "select_a_date",
        )

    def __init__(self, *args, **kwargs):
        super(GetDateForEventForm, self).__init__(*args, **kwargs)
        self.fields['select_a_date'].widget = forms.Select(choices=kwargs['initial']['select_a_date'])
        self.fields['select_a_date'].required = False


class ClientOnlyCreateForm(forms.ModelForm):
    select_a_date = forms.DateField(
        widget=forms.SelectDateWidget()
        )
    class Meta:
        model = ClientEvent
        fields = (
            "user_client", "client_service", "staff", "select_a_date"
        )
        widgets = {
            'user_client': forms.HiddenInput(),
            }


class StaffEventUpdateForm(forms.ModelForm):
    class Meta:
        model = StaffEvent
        fields = (
            "staff_activity", "start", "end", "cancelled"
        )
        # widgets = {'image': forms.Select(attrs={'rows':2,}), }
    
    # def clean_item(self):
    #     """
    #     Handles validation.
    #     """
    #     return string.capwords(self.cleaned_data["item"])


# class ProductUpdateForm(ProductCreateForm):
#     pass
 

# class ImageUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ("image",)  


# class ItemAddDamagedForm(forms.Form):
#     damaged_or_lost = forms.IntegerField(label='Quantity of damaged or lost?')


# class ItemAddedForm(forms.Form):
#     added = forms.IntegerField(label='Add additional to stock?')


# class DiscontinueItemForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ("discontinued",)
