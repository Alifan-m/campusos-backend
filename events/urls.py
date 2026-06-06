from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventListView.as_view()),
    path('<int:pk>/', views.EventDetailView.as_view()),
    path('<int:pk>/rsvp/', views.EventRSVPToggleView.as_view()),
]
