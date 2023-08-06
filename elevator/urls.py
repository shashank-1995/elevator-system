from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ElevatorViewSet, BuildingViewSet

router = DefaultRouter()
router.register(r'elevators', ElevatorViewSet)
router.register(r'building', BuildingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]