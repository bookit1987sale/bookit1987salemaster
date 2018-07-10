from django.urls import path

from .views import (
    CompanyUpdate,
    DayList,    
    DayUpdate
)
# get_day

app_name = 'consortium'
urlpatterns = [
    path('hours_of_operation/', DayList.as_view(),
        name="work_days"),
    # path('<slug:slug>/avail/', AvailabilityList.as_view(),
    #     name="staff_avail"),
    # path('all_events/', AllEventList.as_view(),
    #     name="all_event_list"),
    # path('add_client_appt/', ClientApptCreate.as_view(),
    #     name="add_client_appt"),
    path('<int:pk>/update/', CompanyUpdate.as_view(),
        name="company_details"),
    # path('staff_event/<int:pk>/update/', StaffEventUpdate.as_view(),
    #     name="staff_event_update"),
    # path('find/<slug:service>/<slug:client>/<slug:staff>/<str:date>/', AvailForAppointmentList.as_view(),
    #     name="avail_appt_list"),
    # path('<str:start>/<slug:sel_ser>/<slug:staff>/<slug:client>/create/', ClientEventCreate.as_view(),
    #     name="client_event_create"),
    path('<int:pk>/day_update/', DayUpdate.as_view(),
        name="get_day"),
    # url(r'^base/(?P<slug>[-\w]+)/update/$', BaseTypeUpdate.as_view(),
    #     name="service_update"),

    # url(r'^service/manage/(?P<slug>[-\w]+)/$', manage_service,
    #     name="service_manage"),
]