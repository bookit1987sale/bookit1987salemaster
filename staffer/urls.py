from django.urls import path, re_path

from .views import SignupStaffView, StaffList, StaffUpdate
# from event.views import AvailabilityList


app_name = 'staff'
urlpatterns = [
    # path('<slug:slug>/availability/', AvailabilityList.as_view(),
    #     name="staff_avail"),
    path('all_staff/', StaffList.as_view(),
        name="all_staff"),
    path('add_staff/', SignupStaffView.as_view(),
        name="add_staff"),
    path('<int:pk>/update/', StaffUpdate.as_view(),
        name="staff_update"),
    # path('staff_event/<int:pk>/update/', StaffEventUpdate.as_view(),
    #     name="staff_event_update"),
    # path('find/<slug:service>/<slug:client>/<slug:staff>/<str:date>/', AvailForAppointmentList.as_view(),
    #     name="avail_appt_list"),
    # path('<str:start>/<slug:sel_ser>/<slug:staff>/<slug:client>/create/', ClientEventCreate.as_view(),
    #     name="client_event_create"),
    # url(r'^base/(?P<slug>[-\w]+)/update/$', BaseTypeUpdate.as_view(),
    #     name="service_update"),

    # url(r'^service/manage/(?P<slug>[-\w]+)/$', manage_service,
    #     name="service_manage"),
]