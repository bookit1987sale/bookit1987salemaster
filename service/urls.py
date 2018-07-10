
from django.urls import path, re_path

from .views import (
    ServiceList, ServiceUpdate, ServiceCreate
    # BranchList, BranchCreate, BranchUpdate, BaseTypeCreate,
    # BaseTypeDetail, BaseTypeUpdate, manage_service
)


app_name = 'service'
urlpatterns = [
    re_path(r'^services/$', ServiceList.as_view(),
        name="service_list"),
    re_path(r'^create/$', ServiceCreate.as_view(),
        name="service_create"),
    re_path(r'^(?P<slug>[-\w]+)/update/$', ServiceUpdate.as_view(),
        name="service_update"),

    # url(r'^base/(?P<slug>[-\w]+)/create/$', BaseTypeCreate.as_view(),
    #     name="service_create"),
    # url(r'^base/(?P<slug>[-\w]+)/$', BaseTypeDetail.as_view(),
    #     name="service_detail"),
    # url(r'^base/(?P<slug>[-\w]+)/update/$', BaseTypeUpdate.as_view(),
    #     name="service_update"),

    # url(r'^service/manage/(?P<slug>[-\w]+)/$', manage_service,
    #     name="service_manage"),
]