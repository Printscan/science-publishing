from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Work


@receiver(pre_delete, sender=Work)
def cleanup_work_dependencies(sender, instance, **kwargs):
    document_field = getattr(instance, 'document', None)
    if document_field and hasattr(document_field, 'delete'):
        document_field.delete(save=False)
