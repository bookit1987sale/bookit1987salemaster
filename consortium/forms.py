import string
import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
# from django.forms.models import inlineformset_factory
# from django.forms.formsets import BaseFormSet, formset_factory
# from django.utils.translation import ugettext_lazy as _
from .models import Hours
# from source_utils.form_mixins import check_name
from source_utils.time_selector import select_time_options

# from django.forms.models import BaseInlineFormSet


# class BranchForm(forms.ModelForm):
#     category = forms.CharField(
#         label=_("Branch"),
#     )
#     class Meta:
#         model = Branch
#         fields = ('category',)
        
#     def clean_category(self):
#         """
#         Handles validation and capitilize entries.
#         """
#         return check_name(self.cleaned_data["category"])


# class BaseForm(forms.ModelForm):
#     category = forms.CharField(
#         label=_("Service"),
#     )
#     class Meta:
#         model = Base
#         fields = ('branch', 'category')
#         widgets = {'branch': forms.HiddenInput(),}
        
#     def clean_category(self):
#         """
#         Handles validation and capitilize entries.
#         """
#         return self.cleaned_data["category"]


class HoursForm(forms.ModelForm):
    class Meta:
        model = Hours
        fields = (
            "day", "start",
            "end", "closed"
            )

    def __init__(self, *args, **kwargs):
        super(HoursForm, self).__init__(*args, **kwargs)
        times = {}
        times['start'] = "4:00 AM"
        times['end'] = "11:00 PM"
        times['step'] = 15
        self.fields['start'].widget = forms.Select(
            choices=select_time_options(
                company = times, option=1
            )
        )
        self.fields['end'].widget = forms.Select(
            choices=select_time_options(
                times
            )
        )

    def clean(self):
        if self.cleaned_data["closed"] == False:
            if self.cleaned_data["start"] and self.cleaned_data["end"]:
                if datetime.datetime.strptime(
                    self.cleaned_data["start"],
                    "%I:%M %p") >= datetime.datetime.strptime(
                            self.cleaned_data["end"],
                                "%I:%M %p"
                                ):
                    raise forms.ValidationError("End time must exeed start time.")
            else:
                if not self.cleaned_data["start"] or not self.cleaned_data["end"]:
                    raise forms.ValidationError("If not closed, valid start and end times are required.")
        return self.cleaned_data

