from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ElevatorViewSet, FloorViewSet, BuildingViewSet

router = DefaultRouter()
router.register(r'elevators', ElevatorViewSet)
router.register(r'floors', FloorViewSet)
router.register(r'building', BuildingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]