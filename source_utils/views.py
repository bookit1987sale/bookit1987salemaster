import datetime

from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404 #, render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


from service.models import Service, Branch
from service.forms import ServiceForm
from consortium.models import Company
from staffer.models import StaffMember
from event.models import ClientEvent, StaffEvent, SecondPartEvent


class HomeDetail(ListView):
    model = Service
    context_object_name = "services"
    template_name = "homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = get_object_or_404(Company, pk=1)
        context['nowr'] = datetime.datetime.now()
        the_day = 0
        try:
            the_day = self.kwargs['day']
        except:
            pass
        if int(the_day) == 0:
            new_date = datetime.date.today()
            context['real_date'] = the_day
            context['the_day'] = 'Today'
        elif int(the_day) < 0:
            new_date = datetime.date.today() - datetime.timedelta(
                days=abs(int(the_day))
                )           
            context['real_date'] = the_day
            context['the_day'] = new_date
            if int(the_day) == -1:
                context['the_day'] = 'Yesterday'
        else:
            new_date = datetime.date.today() + datetime.timedelta(
                days=int(the_day)
                )
            context['real_date'] = the_day
            context['the_day'] = new_date
            if int(the_day) == 1:
                context['the_day'] = 'Tomorrow'
        if self.request.user.is_staff:
            if self.request.user.account.is_manager:
                events_today = ClientEvent.objects.filter(
                    start__date=new_date
                )
                second_events_today = SecondPartEvent.objects.filter(
                    start__date=new_date
                    )
                my_events_today = events_today.filter(
                    staff__base_account__user=self.request.user
                    )
                my_second_events_today = second_events_today.filter(
                    staff__base_account__user=self.request.user
                    )
                all_events_today = list(events_today) + list(second_events_today)
                context['all_staff_events_today'] = sorted(
                    all_events_today,
                    key=lambda x: x.start
                    )
                all_my_events_today = list(my_events_today) + list(my_second_events_today)
                context['all_my_events_today'] = sorted(
                    all_my_events_today,
                    key=lambda x: x.start
                    )
            else:
                my_events_today = ClientEvent.objects.filter(
                    start__date=new_date,
                    staff__base_account__user=self.request.user
                )
                my_second_events_today = SecondPartEvent.objects.filter(
                    start__date=new_date,
                    staff__base_account__user=self.request.user
                    )
                all_my_events_today = list(my_events_today) + list(my_second_events_today)
                context['all_my_events_today'] = sorted(
                    all_my_events_today,
                    key=lambda x: x.start
                    )
        else:
            if self.request.user.is_authenticated:
                context['my_personal_booking'] = ClientEvent.objects.filter(
                    start__gte=datetime.datetime.now(),
                    user_client__base_account__user=self.request.user
                    )
                context['this_user'] = self.request.user
            context['staff'] = StaffMember.objects.filter(
                base_account__user__is_active=True
                )
            context['service_branches'] = Branch.objects.filter(
                service_no_longer_available=False
                )
            context['popular_services'] = Service.objects.filter(
                popular=True
                )
        return context

