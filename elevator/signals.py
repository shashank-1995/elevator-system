from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Elevator
import json

@receiver(post_save, sender=Elevator)
def update_elevator_status_cache(sender, instance, **kwargs):
    # Update the cache for display_status when an Elevator is saved or updated
    cache_key = f"elevator:{instance.id}:status"
    status =  {
                'id': instance.id,
                'name': instance.name,
                'current_floor': instance.current_floor,
                'is_door_open': instance.is_door_open,
                'is_operational': instance.is_operational
            }
    # Cache the status data for future access
    cache.set(cache_key,status)