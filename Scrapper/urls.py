from django.urls import path

from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path("insertDataView", views.insertDataView, name="insertDataView"),
  path("fetchDatabase", views.fetchDatabase, name="fetchDatabase"),
]