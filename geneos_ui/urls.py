from django.urls import path

from . import views

app_name = "geneos_ui"

urlpatterns = [
    path("", views.catalog, name="catalog"),
]
