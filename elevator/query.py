from django.db import models
from django.utils import timezone

class BaseModelQuerySet(models.QuerySet):

    def update(self, **kwargs):
        kwargs.update(updated=timezone.now())
        return super().update(**kwargs)
    update.alters_data = True

class SoftDeleteQuerySet(models.query.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        qs.update(is_deleted=False)

