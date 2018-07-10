import datetime

from django.shortcuts import render
from django.db.models import Q

from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404 #, render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from service.models import Service, Branch
from service.forms import ServiceForm
from consortium.models import Company
from staffer.models import StaffMember
from event.models import ClientEvent, StaffEvent
from service.serializers import ServicesSerializer

class ServiceList(ListView):
    model = Service
    template_name = "service/service_list.html"
    title = "Services"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.all()
        for service in services:
            service.save()
        context['title'] = self.title
        context['button'] = "Update"
        context['company'] = get_object_or_404(Company, pk=1)
        context['staff'] = StaffMember.objects.filter(base_account__user__is_active=True)
        context['service_branches'] = Branch.objects.filter(service_no_longer_available=False)
        context['popular_services'] = Service.objects.filter(popular=True)
        return context


class ServiceUpdate(UpdateView, SuccessMessageMixin):
    model = Service
    template_name = "form.html"
    success_message = "%(service)s was successfully updated"
    title = "Update Service"
    form_class = ServiceForm
    success_url = reverse_lazy('service:service_list')

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            service=self.object.retail_service,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.all()
        for service in services:
            service.save()
        context['title'] = self.title
        context['button'] = "Update"
        context['company'] = get_object_or_404(Company, pk=1)
        context['staff'] = StaffMember.objects.filter(base_account__user__is_active=True)
        context['service_branches'] = Branch.objects.filter(service_no_longer_available=False)
        context['popular_services'] = Service.objects.filter(popular=True)
        return context


class ServiceCreate(CreateView, SuccessMessageMixin):
    model = Service
    template_name = "form.html"
    form_class = ServiceForm
    success_url = reverse_lazy('service:service_list')
    success_message = "%(service)s was successfully created"
    title = "New Service"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            service=self.object.retail_service,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['button'] = "Create"
        context['company'] = get_object_or_404(Company, pk=1)
        return context


# API Views
class GetEventApi(APIView):

    def get(self, request, format=None):
        params = self.request.query_params
        # print(params)
        # event_params = json.loads(params['staff'])
        service = get_object_or_404(Service, retail_service=params['service'])
        return Response({ 
            'service_time': service.minutes
            })


class ServicesViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Service.objects.filter(
        staff_trained_for=True,
        service_no_longer_available=False
        )
    serializer_class = ServicesSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        services = Service.objects.all()
        for service in services:
            service.save()
        queryset = super().get_queryset()
        return queryset
        # params = self.request.query_params
        # if params['is_staff'] == 'true':
        #     if params['next']  == 'true':
        #         return ClientEvent.objects.filter(
        #             staff__base_account=params['user_pk'],
        #             end__gt=datetime.datetime.now()
        #             )
        #     elif params['day'] != 'false':
        #         sel_day = datetime.datetime.strptime(
        #         params['day'],
        #         "%m-%d-%Y"
        #         )
        #         return ClientEvent.objects.filter(
        #             staff__base_account=params['user_pk'],
        #             # end__lt=sel_day,
        #             # end__gt=sel_day + datetime.timedelta(days=1)
        #             start__date=sel_day
        #             )
        #     else:
        #         return ClientEvent.objects.filter(
        #             staff__base_account=params['user_pk']
        #             )
        # else:
        #     if params['next']  == 'true':
        #         return ClientEvent.objects.filter(
        #             user_client__base_account=params['user_pk'],
        #             end__gt=datetime.datetime.now()
        #             )
        #     else:
        #         return ClientEvent.objects.filter(
        #             user_client__base_account=params['user_pk']
        #             )
