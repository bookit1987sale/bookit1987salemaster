from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers
# from rest_framework.authtoken import views
from account.views import SignUpAPI, PasswordResetTokenAPI, PasswordResetAuthAPI
from consumer.views import ClientMemberViewSet
from service.views import ServicesViewSet, GetEventApi
from staffer.views import StaffMemberViewSet
from event.views import (
    ClientEventViewSet,
    GetDateForEventApiList,
    GetAvailForAppointmentList,
    EventCreateAPI,
    EventUpdateAPI,
    EventCancelAPI
    )
from consortium.views import CompanyDetailsViewSet
from source_utils.views import HomeDetail
from source_utils.permission_mixins import CustomAuthToken, ChangePasswordView
# from rest_framework.authtoken.views import ChangePasswordView

from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'services', ServicesViewSet)
router.register(r'recent_appointments', ClientEventViewSet)
router.register(r'active_staff', StaffMemberViewSet)
router.register(r'company_details', CompanyDetailsViewSet)
# router.register(r'server_time', GetDateForEventApiList, base_name='server_time')


from rest_auth.views import LoginView


urlpatterns = [
    path("", HomeDetail.as_view(), name="home"),
    re_path(r'^schedule/(?P<day>-?\d+)/$', HomeDetail.as_view(), name="home_schedule"),
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
    path('sign_up/', SignUpAPI.as_view(), name='sign_up'),
    path('get_reset_pin/', PasswordResetTokenAPI.as_view(), name='get_reset_pin'),
    path('get_reset_auth/', PasswordResetAuthAPI.as_view(), name='get_reset_auth'),
    # url(r'^$',EmployeeTemplateView.as_view(emp='employees')
    path('available_appt_dates/', GetDateForEventApiList.as_view(), name='available_appt_dates'),
    path('available_appt_times/', GetAvailForAppointmentList.as_view(), name='available_appt_times'),
    path('create_event_api/', EventCreateAPI.as_view(), name='create_event_api'),
    path('update_event_api/', EventUpdateAPI.as_view(), name='update_event_api'),
    path('cancel_event_api/', EventCancelAPI.as_view(), name='cancel_event_api'),
    path('get_event_api/', GetEventApi.as_view(), name='get_event_api'),
    path('rest-auth/login/', LoginView.as_view(), name='rest_login'),
    path('reset_password/', ChangePasswordView.as_view(), name='reset_password'),

    path("service/", include("service.urls")),
    path("event/", include("event.urls")),
    path("client/", include("consumer.urls")),
    path("staff_schedule/", include("staff_sced.urls")),
    path("staff/", include("staffer.urls")),
    path("company/", include("consortium.urls")),

    path("client_users/<str:username>/<str:hello>/", ClientMemberViewSet.as_view({'get': 'list'})),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# from rest_framework.authtoken import views
# urlpatterns += [
#     url(r'^api-token-auth/', views.obtain_auth_token)
# ]