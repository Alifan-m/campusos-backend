from django.urls import path
from . import views

urlpatterns = [
    path('', views.MapLocationListView.as_view()),
]
