from django.urls import path, re_path

from .views import (
    ClientDetail
    # MyEventList, ClientEventUdate
    # BranchList, BranchCreate, BranchUpdate, BaseTypeCreate,
    # BaseTypeDetail, BaseTypeUpdate, manage_service
)


app_name = 'consumer'
urlpatterns = [
    # re_path(r'^my_events/$', MyEventList.as_view(),
    #     name="my_event_list"),
    # # re_path(r'^create/$', ServiceCreate.as_view(),
    # #     name="service_create"),
    # path('<int:pk>/update/', ClientEventUdate.as_view(),
    #     name="event_detail"),

    # url(r'^base/(?P<slug>[-\w]+)/create/$', BaseTypeCreate.as_view(),
    #     name="service_create"),
    path('<slug:slug>/', ClientDetail.as_view(),
        name="client_detail"),
    # url(r'^base/(?P<slug>[-\w]+)/update/$', BaseTypeUpdate.as_view(),
    #     name="service_update"),

    # url(r'^service/manage/(?P<slug>[-\w]+)/$', manage_service,
    #     name="service_manage"),
]