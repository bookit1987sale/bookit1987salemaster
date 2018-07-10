from django.shortcuts import render

from django.views.generic import DetailView

from consumer.models import ClientMember
from event.models import ClientEvent
from rest_framework import viewsets
from consumer.serializers import ClientMemberSerializer


class ClientDetail(DetailView):
    model = ClientMember
    # template_name = "product/item_detail.html"
    # def get_appts_for_client(self):
    #     return ClientEvent.objects.filter(user_client__user=self.base_account.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_events'] = ClientEvent.objects.filter(
            user_client=self.object).order_by('-start')
        # print(context['client_events'])
        return context

class ClientMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ClientMember.objects.all().order_by('last_name')
    serializer_class = ClientMemberSerializer

