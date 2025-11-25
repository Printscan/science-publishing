from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import (
    EditorialRole,
    EditorialTask,
    EditorialTaskMessage,
    UserProfileRole,
    Work,
)


def _work_title(work):
    return work.discipline_name or work.short_description or str(work.id)


def _chief_users():
    assignments = (
        UserProfileRole.objects.select_related('profile__user').filter(role__code=EditorialRole.Code.CHIEF_EDITOR)
    )
    for assignment in assignments:
        user = getattr(assignment.profile, 'user', None)
        if user:
            yield user


@receiver(post_save, sender=Work)
def create_initial_chief_task(sender, instance, created, raw=False, **kwargs):
    if raw or not created:
        return

    if instance.status not in (Work.Status.DRAFT, Work.Status.PENDING_CHIEF_REVIEW):
        return

    # если уже есть активная задача у главного редактора по этой работе — повторно не создаём
    existing = EditorialTask.objects.filter(
        work=instance,
        closed_at__isnull=True,
        recipient__science_publishing_profile__roles__code=EditorialRole.Code.CHIEF_EDITOR,
    ).exists()
    if existing:
        return

    message = f'Работа <{_work_title(instance)}> поступила в рассмотрение.'
    sender_user = getattr(getattr(instance, 'profile', None), 'user', None)

    for chief in _chief_users():
        task = EditorialTask.objects.create(
            work=instance,
            recipient=chief,
            sender=sender_user,
            subject=f'Задача по работе <{_work_title(instance)}>',
            message=message,
            status=EditorialTask.Status.NEW,
            payload={
                'work_status': instance.status,
                'note': message,
            },
        )
        if sender_user:
            EditorialTaskMessage.objects.create(task=task, author=sender_user, content=message)


@receiver(pre_delete, sender=Work)
def cleanup_work_dependencies(sender, instance, **kwargs):
    document_field = getattr(instance, 'document', None)
    if document_field and hasattr(document_field, 'delete'):
        document_field.delete(save=False)

    try:
        tasks_qs = instance.tasks.all()
        if tasks_qs.exists():
            for task in tasks_qs:
                task.messages.all().delete()
            tasks_qs.delete()
    except Exception:
        # даже при ошибках чистки задач не прерываем удаление работы
        pass
