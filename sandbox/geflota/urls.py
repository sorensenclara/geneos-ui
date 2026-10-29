from django.urls import path

from . import views

app_name = "geflota"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("vehiculos/", views.vehiculos, name="vehiculos"),
    path("s/<slug:seccion>/", views.pendiente, name="pendiente"),
]
