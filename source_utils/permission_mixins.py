import datetime

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404

# from schedule.models import Event
# from schedule.periods import Day

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from account.models import Account
from django.contrib.auth.models import User

class ChangePasswordView(APIView):

    def post(self, request, *args, **kwargs):
        response = "500"
        try:
            params = request.data
            account = Account.objects.get(pk=params['acct_pk'])
            account.user.set_password(params['new_password'])
            account.user.save()
            response = "200"
            return Response({ 
                'response': response
                })
        except:
            return Response({ 
                'response': response
                },
                status=status.HTTP_404_NOT_FOUND)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Important pk
        account = get_object_or_404(Account, user=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'key': token.key,
            'created': created,
            'acct_pk': account.pk,
            # 'username': account.user.username,
            # 'email': account.user.email,
            'phone_number': account.main_phone,
            # 'second_phone': account.user.alt_phone_number,
            'is_staff': account.user.is_staff,
            'is_active': account.user.is_active,
            'date_joined': account.user.date_joined,
            'first_name': account.user.get_short_name(),
            'full_name': account.user.get_full_name()
        })


class TemporaryPassWordTemplateView(TemplateView):

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.__str__() == "AnonymousUser" or \
        request.user.account.initial_password == None or\
        request.user.is_superuser:
            return super(TemplateView, self).dispatch(request, 
                *args, **kwargs)
        else:
            return redirect('temp_password_change')        


class MyScheduleList:
    
    def get_my_schedule(self):
        today = timezone.now()
        start = today - datetime.timedelta(days=367)
        end = today + datetime.timedelta(days=1)
        events = Event.objects.filter(start__range=[start, end]).filter(staff=self.request.user)
        today_events = Day(events, today)
        return today_events.get_occurrences()


class SuperUserCheckMixin(MyScheduleList):
    title = None
    url_insert = None
    permissions = ['is_superuser',]
    user_check_failure_path = '500'

   
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_active or request.user.account.initial_password:
            return redirect('temp_password_change')
        perm_dict = {
            'is_superuser': self.request.user.is_superuser,
            'is_manager': self.request.user.is_manager,
            'is_financial': self.request.user.is_financial,
            'is_warehouse': self.request.user.is_warehouse,
            'is_maintenance': self.request.user.is_maintenance,
            'is_staff': self.request.user.is_staff,
            'is_service': self.request.user.is_service,
            }
        if request.user.is_active:
            for priviledge in self.permissions:
                if perm_dict[priviledge]:
                    return super(SuperUserCheckMixin, self).dispatch(request, 
                    	*args, **kwargs)
        return redirect(self.user_check_failure_path)

    def get_context_data(self, **kwargs):
        context = super(SuperUserCheckMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['url_insert'] = self.url_insert
        context['my_schedule'] = self.get_my_schedule()
        return context


class ManagerCheckMixin(SuperUserCheckMixin):
    permissions = ['is_superuser', 'is_manager']


class StaffCheckMixin(SuperUserCheckMixin):
    permissions = ['is_superuser', 'is_staff']


class WarehouseAndManagerCheckMixin(SuperUserCheckMixin):
    permissions = ['is_superuser', 'is_manager', 'is_warehouse']
 

class MaintenanceAndManagerCheckMixin(SuperUserCheckMixin):
    permissions = ['is_superuser', 'is_manager', 'is_maintenance']


class FinanceCheckMixin(SuperUserCheckMixin):
    permissions = ['is_superuser', 'is_financial']
