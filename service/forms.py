import string

from django import forms
# from django.forms.models import inlineformset_factory
# from django.forms.formsets import BaseFormSet, formset_factory
# from django.utils.translation import ugettext_lazy as _
from .models import Service
# from source_utils.form_mixins import check_name

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


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = (
            "service_branch", "retail_service",
            "minutes", "cost", "service_no_longer_available", 
            "overlap_from", "overlap_minutes", "overlap_minutes"
        )
        widgets = {'base': forms.HiddenInput(),}