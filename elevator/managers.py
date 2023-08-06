from django.db import models
from elevator.query import BaseModelQuerySet, SoftDeleteQuerySet

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return BaseModelQuerySet(self.model, using=self._db)

    def update(self, payload, **kwargs):
        return self.get_queryset().update(**kwargs)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        query = SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=False)
        return query

class DeletedManager(models.Manager):

    def get_queryset(self):
        query = SoftDeleteQuerySet(self.model, self._db).filter(is_deleted=True)
        return query

class ShowAllManager(models.Manager):
    def get_queryset(self):
        query = SoftDeleteQuerySet(self.model, self._db).filter()
        return query

