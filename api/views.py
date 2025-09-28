from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Trip
from .serializers import TripSerializer
from .hos import generate_hos_schedule
from datetime import datetime
import requests
import polyline
from django.conf import settings

class TripCreateView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

@api_view(["GET"])
def get_trip_route(request, pk):
    trip = Trip.objects.get(pk=pk)

    ORS_API_KEY = settings.ORS_API_KEY   
    ORS_URL = settings.ORS_URL


    # --- helper: geocode location name into coordinates ---
    def geocode(address):
        url = "https://api.openrouteservice.org/geocode/search"
        params = {"api_key": ORS_API_KEY, "text": address}
        r = requests.get(url, params=params)
        data = r.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords  # [lon, lat]

    start_coords = geocode(trip.current_location)
    pickup_coords = geocode(trip.pickup_location)
    dropoff_coords = geocode(trip.dropoff_location)

    # --- route request with waypoints ---
    body = {"coordinates": [start_coords, pickup_coords, dropoff_coords]}
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    r = requests.post(ORS_URL, json=body, headers=headers)
    route = r.json()

    if "routes" not in route:
        return Response({
            "error": "ORS routing failed",
            "details": route
        }, status=400)


    summary = route["routes"][0]["summary"]
    distance_km = summary["distance"] / 1000
    duration_hr = summary["duration"] / 3600

    coords = polyline.decode(route["routes"][0]["geometry"])


    return Response({
        "start": trip.current_location,
        "pickup": trip.pickup_location,
        "dropoff": trip.dropoff_location,
        "distance_km": round(distance_km, 2),
        "duration_hours": round(duration_hr, 2),
        "geometry": coords
    })

@api_view(["GET"])
def get_trip_logs(request, pk):
    trip = Trip.objects.get(pk=pk)
    schedule = generate_hos_schedule(datetime.now(), drive_hours=9.5)
    return Response(schedule)
