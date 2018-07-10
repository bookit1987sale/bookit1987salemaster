from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Company, Hours
from .forms import HoursForm
from staffer.models import StaffMember
from staffer.forms import SignUpStaffForm
from rest_framework import viewsets
from source_utils.time_selector import order_weekdays

from consortium.serializers import CompanyDetailsSerializer


# def order_weekdays(days):
#     unordered_days = {}
#     ordered_days = []
#     for day in days:
#         unordered_days[time.strptime(day.day, "%A").tm_wday] = day
#     print(unordered_days)
#     for key in sorted(unordered_days.keys()):
#         ordered_days.append(unordered_days[key])
#     return ordered_days


# class CompanyDetail(TemplateResponseMixin, ContextMixin, View):
#     # model = Details
#     template_name="homepage.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['name'] = "rname"
#         return context
class CompanyUpdate(UpdateView):
    model = Company
    success_message = "%(item)s was successfully updated"
    template_name = "form.html"
    success_url = reverse_lazy('consortium:work_days')
    # form_class = HoursForm
    fields = (
        "company",
        "company_phone",
        "email",
        "owner",
        "street_address",
        "city",
        "state",
        "zip_code",
        "caption",
        "bio",
        "alert",
        "appt_step",
        "work_step"
    	)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "{} details".format(
            self.object.company
            )
        context['button'] = "Change"
        # context['company'] = get_object_or_404(Company, pk=1)
        return context


class DayUpdate(UpdateView):
    model = Hours
    success_message = "%(item)s was successfully updated"
    template_name = "form.html"
    success_url = reverse_lazy('consortium:work_days')
    form_class = HoursForm

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update hours for {}".format(
            self.object.day
            )
        context['button'] = "Update"
        context['form_warning'] = "Warning, checking 'Closed on this day' will delete all staff availablity hours for " + self.object.day + "!"
        # context['company'] = get_object_or_404(Company, pk=1)
        return context


class DayList(ListView):
    model = Hours
    template_name = "consortium/day_list.html"
    title = "Hours of Operation"
    context_object_name = 'days'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['days'] = order_weekdays(Hours.objects.all())
        return context


#API

class CompanyDetailsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Company.objects.all()
    serializer_class = CompanyDetailsSerializer


