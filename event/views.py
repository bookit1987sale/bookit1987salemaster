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
from rest_framework.generics import CreateAPIView

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
    SecondPartEvent
    )
from staff_sced.models import AvailabilityForDay
from event.forms import (
    ClientEventForm,
    StaffEventUpdateForm,
    ClientEventCreateForm,
    ClientOnlyCreateForm,
    GetClientForEventForm,
    GetDateForEventForm,
    GetStaffForEventForm,
    GetTypeOfEventForm
    )
# from snippets.permissions import IsOwnerOrReadOnly
from event.serializers import ClientEventSerializer, GetAvailDateSerializer, CreateEventSerializer

from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
    )
from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView

# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from rest_auth.views import LogoutView


def get_staffs_schedule(staff, service_time):
    work_on = AvailabilityForDay.objects.filter(staff_member=staff)
    workable = []
    for day in work_on:
        if datetime.datetime.strptime(
            day.scheduled_start,
            "%I:%M %p") + datetime.timedelta(
                minutes=service_time) <= datetime.datetime.strptime(
                    day.scheduled_end,
                        "%I:%M %p"
                        ):
            workable.append(day.day)
    if not workable:
        # print("no hshshs")
        workable.append("Sorry no available days")
    # print(workable, " ppp p ppp ")
    return workable


def get_opened_days():
    open_days_of_week = []
    closed_on = Hours.objects.all()
    for day in closed_on:
        # print(not day.closed)
        if not day.closed:
            open_days_of_week.append(day.day)
    return set(open_days_of_week)


def get_holidays():
    closed = []
    closed_on = Holidays.objects.all()
    for day in closed_on:
        closed.append(day.day.strftime("%Y-%m-%d"))
    return closed


def possible_days(check_these_staff, service_time, switch=False):
    open_company_days = get_opened_days()
    staff_day_set = set()
    for staff in check_these_staff:
        staff_day_set.update(get_staffs_schedule(staff, service_time))
    # print(staff_day_set, " ------")
    open_on_all = open_company_days & staff_day_set
    holidays = get_holidays()    
    now = timezone.now()
    iter_days = 65
    poss_days = []
    today = Hours.objects.filter(day=now.strftime("%A"))
    for day in today:
        if day.closed:
            now += timedelta(days=1)
        else:
            end_of_work_day = datetime.datetime.strptime(day.end, "%I:%M %p")
            current_time = datetime.datetime.strptime(now.strftime("%I:%M %p"), "%I:%M %p")
            if end_of_work_day < (current_time + datetime.timedelta(minutes=service_time)):
                now += timedelta(days=1)
    while iter_days > 0:
        check_day = now.strftime("%Y-%m-%d")
        day_of_week = now.strftime("%A")
        if check_day not in holidays and day_of_week in open_on_all:
            if switch:
                poss_days.append(now.strftime("%A, %b %d %Y"))
            else:
                poss_days.append((check_day, now.strftime("%A, %b %d %Y")))
        now += timedelta(days=1)
        iter_days -= 1
    if switch:
        return poss_days
    else:
        return tuple(poss_days)


def get_qualified_staff(service):
    all_avail_staff = StaffMember.objects.filter(base_account__user__is_active=True)
    poss_staff = [(0, STAFF_TITLE)]
    poss_pks = ""
    for staff in all_avail_staff:
        for skill in staff.skill_set.all():
            if service == skill:
                poss_staff.append((staff.pk, staff.get_friendly_name()))
                poss_pks = poss_pks + str(staff.pk) + " "
                break
    return poss_staff, slugify(poss_pks)


def start_times_no_cons(possible_times, day_start, day_end, service, details, step):
    while add_minutes(day_start, service.minutes) <= day_end:
        next_start = {'start':day_start}
        all_details = {**next_start, **details}      
        possible_times.append(all_details)
        day_start += datetime.timedelta(minutes=step)
    return possible_times

def start_times_w_cons(con_events, day_start, day_end, service, details, step):
    possible_times = []
    second_start_time = service.overlap_from + service.overlap_minutes
    for conflict in con_events:
        if second_start_time == 0:
            while conflict.start >= add_minutes(day_start, service.minutes):
                next_start = {'start':day_start}
                all_details = {**next_start, **details}
                possible_times.append(all_details)
                day_start += datetime.timedelta(minutes=step)
        else:
            while conflict.start >= add_minutes(day_start, service.overlap_from):
                potential = True
                for second_conflict in con_events:
                    if second_conflict.start >= conflict.start:                       
                        if second_conflict.start <= add_minutes(
                                day_start,
                                second_start_time
                                ) < second_conflict.end:
                            potential = False
                            continue
                        if second_conflict.start < add_minutes(
                                day_start,
                                service.minutes
                                ) <= second_conflict.end:
                            potential = False
                            continue
                        if add_minutes(
                                day_start,
                                second_start_time
                                ) <= second_conflict.start < add_minutes(
                                    day_start,
                                    service.minutes
                                    ):
                            potential = False
                            continue
                        if add_minutes(
                                day_start,
                                second_start_time
                                ) < second_conflict.end <= add_minutes(
                                    day_start,
                                    service.minutes
                                    ):
                            potential = False
                            continue
                        if add_minutes(
                                day_start,
                                second_start_time
                                ) <= second_conflict.start and second_conflict.end <= add_minutes(
                                    day_start,
                                    service.minutes
                                    ):
                            potential = False
                            continue
                        if second_conflict.start <= add_minutes(
                                day_start,
                                second_start_time
                                ) and add_minutes(
                                    day_start,
                                    service.minutes
                                    ) <= second_conflict.end:
                            potential = False
                if potential:
                    next_start = {'start':day_start}
                    all_details = {**next_start, **details}
                    possible_times.append(all_details)
                day_start += datetime.timedelta(minutes=step)
        day_start = conflict.end
    start_times_no_cons(
        possible_times,
        day_start,
        day_end,
        service,
        details,
        step
        )
    return possible_times


class GetClientForEvent(FormView):
    success_message = "%(item)s was successfully added"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = GetClientForEventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Select Client and Service"
        context['button'] = "Next"
        # contect['client'] = self.kwargs.get('client')
        return context

    def form_valid(self, form):
        return redirect(reverse("event:add_service_type",
            kwargs={
                'client': form.cleaned_data.get('user_client').base_account.pk,
                'ev_type': 'for_client'
                }
            )
        )


class GetTypeOfEvent(FormView):
    # model = ClientEvent
    success_message = "%(item)s was successfully added"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = GetTypeOfEventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(self.kwargs.get('client'))
        context['title'] = "My Service"
        context['button'] = "Select"
        return context

    def get_initial(self):
        initial = super(GetTypeOfEvent, self).get_initial()
        if self.kwargs.get('ev_type') == 'for_staff':
            try:
                service = ClientEvent.objects.filter(
                    staff_client__base_account__pk=self.kwargs.get('client')).latest('start')
            except:
                service = None
        else:
            try:
                service = ClientEvent.objects.filter(
                    user_client__base_account__pk=self.kwargs.get('client')).latest('start')
            except:
                service = None
        if service == None:
            initial['service'] = ''
        else:
            initial['service'] = service.client_service
        return initial

    def form_valid(self, form):
        if self.kwargs.get('ev_type') == 'for_staff':
            client = get_object_or_404(
                StaffMember,
                base_account__pk=self.kwargs.get('client')
                )
        else:
            client = get_object_or_404(
                ClientMember,
                base_account__pk=self.kwargs.get('client')
                )
        return redirect(reverse("event:add_staff_to_appt",
            kwargs={
                'service': form.cleaned_data.get("client_service").slug,
                'client': self.kwargs.get('client'),
                'ev_type': self.kwargs.get('ev_type')
                }
            )
        )


class GetStaffForEvent(FormView):
    success_message = "%(item)s was successfully added"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = GetStaffForEventForm

    def get_initial(self):
        initial = super(GetStaffForEvent, self).get_initial()
        self.service = get_object_or_404(
            Service,
            slug=self.kwargs.get('service')
            )
        poss_staff, self.poss_pks = get_qualified_staff(self.service)
        initial['poss_staff'] = poss_staff
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_name = get_object_or_404(Account, pk=self.kwargs.get('client'))
        context['titleb'] = "for " + client_name.get_friendly_name()
        context['title'] = self.service.get_short_description()
        context['button'] = STAFF_TITLE
        return context

    def form_valid(self, form):
        # print(form.cleaned_data.get("staff"), "  56565656")
        if form.cleaned_data.get("staff") != '0':
            self.poss_pks = str(form.cleaned_data.get("staff"))

        return redirect(reverse("event:add_date_to_appt",
            kwargs={
                'selected_staff': self.poss_pks,
                'service': self.kwargs.get("service"),
                'client': self.kwargs.get('client'),
                'ev_type': self.kwargs.get('ev_type')
                }
            )
        )


class GetDateForEvent(FormView):
    success_message = "%(item)s was successfully added"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = GetDateForEventForm

    def get_initial(self):
        initial = super(GetDateForEvent, self).get_initial()
        self.service_name = get_object_or_404(Service, slug=self.kwargs.get('service'))
        check_these_staff = []
        if len(self.kwargs.get('selected_staff')) > 0:
            self.staff = "by Any Available Staff"
            all_pks = self.kwargs.get('selected_staff').split('-')
            for pk in all_pks:
                self.staff_name = get_object_or_404(StaffMember, pk=int(pk))
                check_these_staff.append(self.staff_name)
        else:
            self.staff = "Sorry this Service not Available"
        initial['select_a_date'] = possible_days(
            check_these_staff,
            self.service_name.minutes
            )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_name = get_object_or_404(Account, pk=self.kwargs.get('client'))
        context['titleb'] = "for " + client_name.get_friendly_name()
        context['title'] = self.service_name.get_short_description()
        context['titlec'] = self.staff
        context['button'] = "Select Date"
        return context

    def form_valid(self, form):
        return redirect(reverse("event:avail_appt_list",
            kwargs={
                'selected_staff': self.kwargs.get("selected_staff"),
                'date': form.cleaned_data.get("select_a_date"),
                'staff_name': self.staff_name.get_friendly_name(),
                'service': self.kwargs.get("service"),
                'client': self.kwargs.get('client'),
                'ev_type': self.kwargs.get('ev_type')
                }
            )
        )


def get_avail_for_staff_for_day(selected_service, step, staff_this, start_day, details):
    my_client_events = ClientEvent.objects.filter(
        start__date=start_day,
        staff__pk=staff_this
        )
    my_second_client_events = SecondPartEvent.objects.filter(
        start__date=start_day,
        staff__pk=staff_this
        )
    my_events = list(my_client_events) + list(my_second_client_events)
    conflicting_events = sorted(my_events, key=lambda x: x.start)
    day_hours = AvailabilityForDay.objects.filter(
        staff_member__pk=staff_this,
        day=datetime.datetime.strptime(
            start_day,
            "%Y-%m-%d").strftime('%A')
        )
    conflict_hours = StaffEvent.objects.filter(
        staff__pk=staff_this,
        start__date=start_day
        )
    if conflict_hours:
        added_events = list(conflict_hours) + list(conflicting_events)
        conflicting_events = sorted(added_events, key=lambda x: x.start)
    if day_hours:
        day_start, day_end = day_plus_12_time_to_datetime(
            start_day,
            day_hours[0].scheduled_start,
            start_day,
            day_hours[0].scheduled_end
            )
        if conflicting_events:
            return start_times_w_cons(
                conflicting_events,
                day_start,
                day_end,
                selected_service,
                details,
                step
                )
        else:
            possible_times = []
            return start_times_no_cons(
                possible_times,
                day_start,
                day_end,
                selected_service,
                details,
                step
                )


def get_appts_options_for_day(service, start_day, client, ev_type, pks_l, switch=False):
    company = get_object_or_404(Company, pk=1)
    step = company.appt_step
    selected_service = get_object_or_404(
        Service,
        slug=service
        )
    sched_for_these_staff = []
    if switch:
        all_pks = pks_l
    else:    
        all_pks = pks_l.split('-')
    for pk in all_pks:
        staff_name_fr = get_object_or_404(StaffMember, pk=int(pk))
        details = {
            'service':service, 
            'staff_name':staff_name_fr.get_friendly_name(),
            'staff':pk,
            'client':client,
            'ev_type':ev_type
            }
        this_staff_avail = get_avail_for_staff_for_day(
            selected_service,
            step,
            pk,
            start_day,
            details
            )
        if this_staff_avail:
            if sched_for_these_staff:
                for item in this_staff_avail:
                    sched_for_these_staff.append(item)
                sched_for_these_staff = sorted(sched_for_these_staff,
                    key=itemgetter('start')) 
            else:
                sched_for_these_staff = this_staff_avail
    return sched_for_these_staff


class AvailForAppointmentList(ListView):
    model = ClientEvent
    template_name = "event/avail_for_appt_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['day'] = datetime.datetime.strptime(
            self.kwargs['date'],
            "%Y-%m-%d").strftime("%a %b %d %Y")
        return context

    def get_queryset(self):
        return get_appts_options_for_day(
            self.kwargs['service'],
            self.kwargs['date'],
            # self.kwargs['staff_name'],
            self.kwargs['client'],
            self.kwargs['ev_type'],
            self.kwargs.get('selected_staff')
            )


class ClientEventCreate(CreateView):
    model = ClientEvent
    template_name = "form.html"
    form_class = ClientEventCreateForm
    success_url = reverse_lazy('home')

    def get_initial(self): #staff_client
        initial = super(ClientEventCreate, self).get_initial()
        self.service = get_object_or_404(
            Service,
            slug=self.kwargs.get('service')
            )
        initial['client_service'] = self.service
        # client_type = self.kwargs.get('ev_type')
        self.staff = get_object_or_404(
            StaffMember,
            pk=self.kwargs.get('staff'))
        if self.kwargs.get('ev_type') == 'for_staff':
            initial['staff_client'] = get_object_or_404(
                StaffMember,
                base_account__pk=self.kwargs.get('client')
                )
        else:
            initial['user_client'] = get_object_or_404(
                ClientMember,
                base_account__pk=self.kwargs.get('client')
                )
        initial['staff'] = self.staff
        self.start = self.kwargs.get('start')
        initial['start'] = datetime.datetime.strptime(
                self.start,
                "%Y-%m-%d-%H%M%S")
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = StaffMember.objects.filter(
            base_account__user__is_active=True
            )
        context['service_branches'] = Branch.objects.filter(
            service_no_longer_available=False
            )
        context['popular_services'] = Service.objects.filter(
            popular=True
            )
        context['title'] = "Schedule {}".format(
            self.service.get_short_description(),
            )
        client_name = get_object_or_404(Account, pk=self.kwargs.get('client'))
        context['titleb'] = "for " + client_name.get_friendly_name()
        context['titlec'] = "with " + self.staff.get_friendly_name()
        day = datetime.datetime.strptime(
                self.start,
                "%Y-%m-%d-%H%M%S")
        context['titled'] = "{} at {}?".format(
            day.strftime("%a %b %d %Y"),
            day.strftime("%I:%M %p").lstrip('0')
        )
        context['button'] = "Book It"
        context['company'] = get_object_or_404(Company, pk=1)
        return context

    # def form_valid(self, form):
    #     print(form)
    #     return super().form_valid(form)


class AllEventList(ListView):
    model = StaffEvent
    template_name = "event/all_client_events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_client_events = ClientEvent.objects.all()
        all_second_events = SecondPartEvent.objects.all()
        all_events = list(all_client_events) + list(all_second_events)
        context['all_events'] = sorted(all_events, key=lambda x: x.start)
        context['company'] = get_object_or_404(Company, pk=1)
        return context


class MyEventList(ListView):
    model = StaffEvent
    template_name = "event/staff_events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.datetime.now()
        # print(now - datetime.timedelta(days=60))
        sixty_ago = now - datetime.timedelta(days=60)
        my_client_events = ClientEvent.objects.filter(end__lt=now, end__gt=sixty_ago,
            staff__base_account__user=self.request.user, status="Not Complete"
            )
        # my_second_client_events = SecondPartEvent.objects.filter(
        #     staff__base_account__user=self.request.user
        #     )
        # my_events = list(my_client_events) + list(my_second_client_events)
        # print(my_client_events, " dddd")
        context['my_tasks'] = my_client_events
        context['company'] = get_object_or_404(Company, pk=1)
        if not self.request.user.is_staff:
            context['staff'] = StaffMember.objects.filter(
                base_account__user__is_active=True
                )
            context['service_branches'] = Branch.objects.filter(
                service_no_longer_available=False
                )
            context['popular_services'] = Service.objects.filter(popular=True)
        else:
            context['my_weekly_avail'] = AvailabilityForDay.objects.filter(
                staff_member__base_account__user=self.request.user
                )
            context['my_other_events'] = StaffEvent.objects.filter(
                staff__base_account__user=self.request.user
                )
        return context


class ClientEventUpdate(UpdateView):
    model = ClientEvent
    success_message = "%(item)s was successfully updated"
    template_name = "form.html"
    success_url = reverse_lazy('home')
    form_class = ClientEventForm

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update {}".format(
            self.object.get_event_title()
            )
        context['button'] = "Update"
        context['company'] = get_object_or_404(Company, pk=1)
        return context


class StaffEventUpdate(UpdateView):
    model = StaffEvent
    success_message = "%(item)s was successfully updated"
    # url_insert = "product:item_delete"
    template_name = "form.html"
    success_url = reverse_lazy('event:my_event_list')
    form_class = StaffEventUpdateForm

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            item=self.object,
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update {}".format(
            self.object
            )
        context['button'] = "Update"
        context['company'] = get_object_or_404(Company, pk=1)
        return context


# API Views

class GetDateForEventApiList(APIView):

    def get(self, request, format=None):
        params = self.request.query_params
        staff_pks = json.loads(params['staff'])
        avail_staff = []
        discard = ['[', ']', ',']
        # print(staff_pks, "   db")
        for pk in staff_pks:
            if pk not in discard:
                member = get_object_or_404(StaffMember, pk=pk)
                # print(member, " ooooo")
                avail_staff.append(member)

        dates = possible_days(avail_staff, int(params['minutes']), True)
        return Response({ 
            'dates': dates
            })


class GetAvailForAppointmentList(APIView):

    def get(self, request, format=None):
        params = self.request.query_params
        service = get_object_or_404(Service, retail_service=params['service'])
        start_day = datetime.datetime.strptime(params['date'], "%A, %b %d %Y").strftime("%Y-%m-%d")
        times = get_appts_options_for_day(service.slug, start_day, params['client'], params['ev_type'], json.loads(params['staff']), switch=True)
        return Response({ 
            'times': times
            })


class EventCreateAPI(APIView):
    
    def post(self, request, *args, **kwargs):
        params = request.data
        # print(params)
        # staff_pk = json.loads(params['staff'])
        # service = json.loads(params['service'])
        client = get_object_or_404(ClientMember, base_account__pk=params['client'])
        if not client.base_account.user.is_active:
            company = get_object_or_404(Company, pk=1)
            return Response({ 
                'response': 'deactivated',
                'business_phone': company.company_phone,
                'company': company.company
                })
        start = params['date_time'].replace("T"," ")
        if params['ev_type'] == 'for_client':
            user_client_pk = params['client']
        else:
            staff_client_pk = params['client']
        try:
            er = ClientEvent.objects.create(
                client_service=get_object_or_404(Service, retail_service=params['service']),
                staff=get_object_or_404(StaffMember, pk=params['staff']),
                start=datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S"),
                user_client=client
                )
            response = "200"
            print(er, "  yyyy  yyyy")
        except:
            response = "500"
        return Response({ 
            'response': response
            })


class EventUpdateAPI(APIView):
    
    def post(self, request, *args, **kwargs):
        params = request.data
        event = get_object_or_404(ClientEvent, pk=params['event_pk'])
        event.staff = get_object_or_404(
            StaffMember,
            pk=params['staff']
            )
        event.client_service = get_object_or_404(
            Service,
            retail_service=params['service']
            )
        event.start = datetime.datetime.strptime(
            params['date_time'].replace("T"," "),
            "%Y-%m-%d %H:%M:%S"
            )
        if params['ev_type'] == 'for_client':
            event.user_client = get_object_or_404(
                ClientMember,
                base_account__pk=params['client']
                )
            try:
                event.save()                       
                response = "200"
            except:
                response = "500"
        else:
            event.staff_client = get_object_or_404(
                StaffMember,
                base_account__pk=params['client']
                )
            try:
                event.save()                       
                response = "200"
            except:
                response = "500"
        return Response({ 
            'response': response
            })


class ChangePasswordView(APIView):

    def post(self, request, *args, **kwargs):
        # print(request.data)
        event = 'get_object_or_404(ClientEvent, pk=params)'
        # try:
        #     # event.status = 'Cancelled'
        #     # event.save()
        #     response = "200"
        # except:
        #     response = "500"
        return Response({ 
            'response': 'response'
            })


class EventCancelAPI(APIView):

    def post(self, request, *args, **kwargs):
        params = request.data
        # event = get_object_or_404(ClientEvent, pk=params['event_pk'])
        try:
            event = get_object_or_404(ClientEvent, pk=params['event_pk'])
            event.status = 'Cancelled'
            if event.second_event:
                event.second_event.delete()
            event.save()
            response = "200"
        except:
            response = "500"
        return Response({ 
            'response': response
            })


class ClientEventViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = ClientEvent.objects.all()
    serializer_class = ClientEventSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):

        queryset = super().get_queryset()
        params = self.request.query_params
        if params['is_staff'] == 'true':
            if params['next']  == 'true':
                return ClientEvent.objects.filter(
                    staff__base_account=params['acct_pk'],
                    end__gt=datetime.datetime.now()
                    ).exclude(status='Cancelled').order_by('-id')[:10]
            elif params['day'] != 'false':
                sel_day = datetime.datetime.strptime(
                params['day'],
                "%m-%d-%Y"
                )
                return ClientEvent.objects.filter(
                    staff__base_account=params['acct_pk'],
                    start__date=sel_day
                    ).exclude(status='Cancelled').order_by('-id')[:10]
            else:
                return ClientEvent.objects.filter(
                    staff__base_account=params['acct_pk']
                    ).exclude(status='Cancelled').order_by('-id')[:10]
        else:
            if params['next']  == 'true':
                return ClientEvent.objects.filter(
                    user_client__base_account=params['acct_pk'],
                    end__gt=datetime.datetime.now()
                    ).exclude(status='Cancelled').order_by('-id')[:10]
            else:
                return ClientEvent.objects.filter(
                    user_client__base_account=params['acct_pk']
                    ).exclude(status='Cancelled').order_by('-id')[:10]

