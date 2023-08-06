from django.db import models
from elevator.managers import BaseModelManager
import redis
from django.conf import settings

class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()

    class Meta:
        abstract = True

class Elevator(BaseModel):
    name = models.CharField(max_length=100)
    current_floor = models.IntegerField(default=0)
    is_door_open = models.BooleanField(default=False)
    is_operational = models.BooleanField(default=True)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)
    requests = models.JSONField(default=list)
    is_selected = models.BooleanField(default=False)
    direction = models.CharField(max_length=10, choices=[('UP', 'Up'), ('DOWN', 'Down')])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_list = []


    def __str__(self):
        return self.name

    def _get_redis_connection(self):
        return redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

    def display_status(self):
        cache_key = f"elevator:{self.id}:status"
        cache = self._get_redis_connection()

        status = cache.get(cache_key)
        if status is None:
            status = {
                'name': self.name,
                'current_floor': self.current_floor,
                'is_door_open': self.is_door_open,
                'is_operational': self.is_operational,
                'is_running': self.is_running
            }
            # Cache the status data for future access with a TTL (e.g., 60 seconds)
            cache.set(cache_key, status, timeout=60)

        return status
    
    class Meta:
        ordering = ['created']
        unique_together = (('name', 'building'), )

class Floor(BaseModel):
    number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Floor {self.number}"

class Building(BaseModel):
    name =  models.CharField(max_length=512, null=True, blank=True, db_index=True)
    
    def __str__(self):
        return f"Building {self.name}"