from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Elevator

@receiver(post_save, sender=Elevator)
def update_elevator_status_cache(sender, instance, **kwargs):
    # Update the cache for display_status when an Elevator is saved or updated
    cache_key = f"elevator:{instance.id}:status"
    status =  {
                'name': instance.name,
                'current_floor': instance.current_floor,
                'is_door_open': instance.is_door_open,
                'is_operational': instance.is_operational,
                'is_running': instance.is_running
            }
    # Cache the status data for future access with a TTL (e.g., 60 seconds)
    cache.set(cache_key, status, timeout=60)