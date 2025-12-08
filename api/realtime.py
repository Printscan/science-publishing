from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from modules.science_publishing.api.serializers import WorkChatMessageSerializer
from modules.science_publishing.api.models import EditorialRole, UserProfile, Work

# Группа для персональных уведомлений пользователя
def _notification_group(user_id):
    return f'science_publishing_notifications_{user_id}'


def _work_title(work: Work):
    return getattr(work, 'discipline_name', None) or getattr(work, 'short_description', None) or str(work.id)


def collect_work_user_ids(work: Work):
    """Возвращает id пользователей, для которых актуальны события по работе."""
    user_ids = set()
    author_user = getattr(getattr(work, 'profile', None), 'user', None)
    if author_user and author_user.id:
        user_ids.add(author_user.id)

    editor_user = getattr(getattr(work, 'current_editor', None), 'user', None)
    if editor_user and editor_user.id:
        user_ids.add(editor_user.id)

    chiefs = (
        UserProfile.objects.filter(roles__code=EditorialRole.Code.CHIEF_EDITOR)
        .values_list('user_id', flat=True)
    )
    user_ids.update([uid for uid in chiefs if uid])
    return user_ids
_collect_work_user_ids = collect_work_user_ids  # обратная совместимость


def broadcast_notifications(user_payload_pairs):
    """
    Отправляет произвольные payload'ы в персональные группы пользователей.
    user_payload_pairs: Iterable[(user_id, payload_dict)]
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    for user_id, payload in user_payload_pairs:
        if not user_id or not payload:
            continue
        async_to_sync(channel_layer.group_send)(
            _notification_group(user_id),
            {
                'type': 'notification.message',
                'payload': payload,
            },
        )


def broadcast_chat_message(message):
    """
    Отправляет созданное сообщение чата всем подписчикам websocket-группы работы.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    serializer = WorkChatMessageSerializer(message)
    async_to_sync(channel_layer.group_send)(
        f'science_publishing_chat_{message.work_id}',
        {
            'type': 'chat.message',
            'payload': serializer.data,
        },
    )


def broadcast_chat_notification(message, *, skip_user_ids=None):
    """
    Отправляет уведомление о новом сообщении в чат всем, кто связан с работой.
    """
    skip_user_ids = set(skip_user_ids or [])
    work = getattr(message, 'work', None)
    if not work:
        return

    recipients = _collect_work_user_ids(work) - skip_user_ids
    if not recipients:
        return

    title = _work_title(work)
    content = getattr(message, 'content', '') or 'Новое сообщение в чате'
    author_user = getattr(getattr(work, 'profile', None), 'user', None)
    author_user_id = getattr(author_user, 'id', None)

    payloads = []
    for user_id in recipients:
        route_name = 'SciencePublishingDrafts' if user_id == author_user_id else 'SciencePublishingTasks'
        payloads.append(
            (
                user_id,
                {
                    'id': str(message.id),
                    'type': 'chat_message',
                    'work_id': str(work.id),
                    'work_title': title,
                    'message': content,
                    'author': getattr(getattr(message, 'author', None), 'username', None),
                    'route_name': route_name,
                    'route_params': {},
                    'route_query': {'work': str(work.id), 'tab': 'chat'},
                },
            )
        )
    broadcast_notifications(payloads)


def broadcast_work_published(work, *, note=None):
    """Уведомляет автора и назначенного редактора о публикации работы."""
    if not work:
        return
    title = _work_title(work)
    content = note or f'Работа "{title}" опубликована.'
    author_user = getattr(getattr(work, 'profile', None), 'user', None)
    editor_user = getattr(getattr(work, 'current_editor', None), 'user', None)

    payloads = []
    if author_user and author_user.id:
        payloads.append(
            (
                author_user.id,
                {
                    'id': f'published-{work.id}',
                    'type': 'work_published',
                    'work_id': str(work.id),
                    'work_title': title,
                    'message': content,
                    'route_name': 'SciencePublishingPublications',
                    'route_params': {},
                    'route_query': {'work': str(work.id)},
                },
            )
        )
    if editor_user and editor_user.id:
        payloads.append(
            (
                editor_user.id,
                {
                    'id': f'published-editor-{work.id}',
                    'type': 'work_published',
                    'work_id': str(work.id),
                    'work_title': title,
                    'message': content,
                    'route_name': 'SciencePublishingTasks',
                    'route_params': {},
                    'route_query': {'work': str(work.id)},
                },
            )
        )
    if payloads:
        broadcast_notifications(payloads)


def broadcast_editor_assignment(work, editor_profile, *, note=None):
    """Уведомляет редактора о новой назначенной работе."""
    if not work or not editor_profile:
        return
    editor_user = getattr(editor_profile, 'user', None)
    if not editor_user or not editor_user.id:
        return
    title = _work_title(work)
    content = note or f'Вам назначена работа "{title}".'
    broadcast_notifications(
        [
            (
                editor_user.id,
                {
                    'id': f'editor-task-{work.id}',
                    'type': 'editor_task',
                    'work_id': str(work.id),
                    'work_title': title,
                    'message': content,
                    'route_name': 'SciencePublishingTasks',
                    'route_params': {},
                    'route_query': {'work': str(work.id)},
                },
            )
        ]
    )
