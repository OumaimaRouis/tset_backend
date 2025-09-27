from django.urls import path
from .views import TripCreateView, get_trip_route, get_trip_logs

urlpatterns = [
    path('trips/', TripCreateView.as_view(), name='trip-create'),
    path('trips/<int:pk>/route/', get_trip_route, name='trip-route'),
    path('trips/<int:pk>/logs/', get_trip_logs, name='trip-logs'),
]
