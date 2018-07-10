from django.urls import path, re_path

from .views import (
    AllEventList,
    AvailForAppointmentList,
    # AvailabilityList,
    # ClientApptCreate,
    ClientEventCreate,
    ClientEventUpdate,
    GetDateForEvent,
    GetClientForEvent,
    GetTypeOfEvent,
    GetStaffForEvent,
    # MyAvailCreate,
    # MyAvailUpdate,
    MyEventList,    
    StaffEventUpdate
)


app_name = 'event'
urlpatterns = [
    path('my_events/',
        MyEventList.as_view(),
        name="my_event_list"),
    # path('<slug:slug>/avail/',
    #     AvailabilityList.as_view(),
    #     name="staff_avail"),
    path('all_events/',
        AllEventList.as_view(),
        name="all_event_list"),
    path('add/event/',
        GetClientForEvent.as_view(),
        name="start_new_client_appt"),
    path('add/<int:client>/<str:ev_type>/',
        GetTypeOfEvent.as_view(),
        name="add_service_type"),
    path('add/<slug:service>/<int:client>/<str:ev_type>/',
        GetStaffForEvent.as_view(),
        name="add_staff_to_appt"),

    path('add/<str:selected_staff>/<slug:service>/<int:client>/<str:ev_type>/',
        GetDateForEvent.as_view(),
        name="add_date_to_appt"),
    
    path('<int:pk>/update/',
        ClientEventUpdate.as_view(),
        name="event_update"),
    path('staff_event/<int:pk>/update/',
        StaffEventUpdate.as_view(),
        name="staff_event_update"),

    path('find/<str:selected_staff>/<str:date>/<str:staff_name>/<slug:service>/<int:client>/<str:ev_type>/',
        AvailForAppointmentList.as_view(),
        name="avail_appt_list"),

    path('create/<str:start>/<str:staff>/<slug:service>/<int:client>/<str:ev_type>/',
        ClientEventCreate.as_view(),
        name="client_event_create"),
    # path('<int:pk>/avail_update/',
    #     MyAvailUpdate.as_view(),
    #     name="my_avail_update"),
    # path('<int:pk>/avail_create/',
    #     MyAvailCreate.as_view(),
    #     name="avail_create"),



    
    # url(r'^base/(?P<slug>[-\w]+)/update/$', BaseTypeUpdate.as_view(),
    #     name="service_update"),

    # url(r'^service/manage/(?P<slug>[-\w]+)/$', manage_service,
    #     name="service_manage"),
]