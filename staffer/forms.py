from django import forms
# from django.utils import timezone
# from bootstrap_datepicker.widgets import DatePicker
from django.utils.translation import ugettext_lazy as _
from .models import StaffMember
from service.models import Service
# from source_utils.form_mixins import (
#     check_name, 
#     check_phone_options, 
#     company_name_check
# )

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


# class IncidentForm(forms.ModelForm):
#    technician = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=User.objects.all())

#      class Meta:
#         model = Incident
#         fields = [
#                 'technician',
#                 'capa',
#                ]

class StaffUpdateForm(forms.ModelForm):
    skill_set = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=Service.objects.all()
        )
    # email = forms.EmailField(
    #     label=_("Email"),
    #     widget=forms.TextInput(),
    #     required=True
    # )
    # phone_number = forms.IntegerField(
    #     label=_("Phone number"),
    #     required=True
    # )
    # alt_phone_number = forms.IntegerField(
    #     label=_("Phone other"),
    #     # help_text='Not Required',
    #     required=False
    # )
    # first_name = forms.CharField(
    #     label=_("First name"),
    #     max_length=30,
    #     widget=forms.TextInput(),
    #     required=True
    # )
    # last_name = forms.CharField(
    #     label=_("Last name"),
    #     max_length=30,
    #     widget=forms.TextInput(),
    #     required=True
    # )
    # is_manager = forms.BooleanField(
    #     initial=False
    # )
    # is_staff = forms.BooleanField(
    #     initial=False
    # )

    class Meta:
        model = StaffMember
        fields = [
            # 'initial_password',
            'skill_set',
            # 'spouse_name',
            # 'street_address',
            # 'city',
            # 'state',
            # 'zip_code',
            # 'is_staff'
            ]
        # widgets = {
        #     # 'is_staff': forms.HiddenInput(),
        #     # 'initial_password': forms.HiddenInput(),
        #     }


class SignUpStaffForm(forms.ModelForm):
    my_skills = forms.ModelMultipleChoiceField(
    	widget=forms.CheckboxSelectMultiple(),
    	queryset=StaffMember.objects.all()
    	)
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(),
        required=True
    )
    phone_number = forms.IntegerField(
        label=_("Phone number"),
        required=True
    )
    alt_phone_number = forms.IntegerField(
        label=_("Phone other"),
        help_text='Not Required',
        required=False
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )
    is_manager = forms.BooleanField(
    	initial=False
	)
    is_staff = forms.BooleanField(
    	initial=False
    )

    class Meta:
        model = StaffMember
        fields = [
            'initial_password',
            'spouse_name',
            'street_address',
            'city',
            'state',
            'zip_code',
            'my_skills',
            'is_staff'
            ]
        widgets = {
            'is_staff': forms.HiddenInput(),
            'initial_password': forms.HiddenInput(),
            }


