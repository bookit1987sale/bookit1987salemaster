from django.urls import path, re_path

from staff_sced.views import (
    AvailabilityList,
    MyAvailCreate,
    MyAvailUpdate
)


app_name = 'staff_sced'
urlpatterns = [
    path('<slug:slug>/avail/',
        AvailabilityList.as_view(),
        name="staff_avail"),   
    path('<int:pk>/avail_update/',
        MyAvailUpdate.as_view(),
        name="my_avail_update"),
    path('<int:pk>/avail_create/',
        MyAvailCreate.as_view(),
        name="avail_create")
]