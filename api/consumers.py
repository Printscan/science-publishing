import json
from django.db import models

from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from modules.science_publishing.api.models import Work, WorkChatMessage, EditorialRole, UserProfile, WorkChatReceipt
from modules.science_publishing.api.serializers import WorkChatMessageSerializer
from modules.science_publishing.api.realtime import broadcast_notifications, collect_work_user_ids


def _user_has_role(user, role_code):
    try:
        profile = user.science_publishing_profile
    except UserProfile.DoesNotExist:
        return False
    return profile.roles.filter(code=role_code).exists()


def _can_access_chat_sync(user, work: Work) -> bool:
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser or user.is_staff:
        return True
    if getattr(work.profile, 'user', None) == user:
        return True
    if getattr(getattr(work, 'current_editor', None), 'user', None) == user:
        return True
    return any(
        _user_has_role(user, code)
        for code in (
            EditorialRole.Code.CHIEF_EDITOR,
            EditorialRole.Code.ADMINISTRATOR,
            EditorialRole.Code.EDITOR,
        )
    )


class WorkChatConsumer(AsyncJsonWebsocketConsumer):
    group_name: str = ''
    work: Work | None = None
    author_user_id: int | None = None
    editor_user_id: int | None = None
    chief_user_ids: list[int] = []

    async def connect(self):
        user = self.scope.get('user', AnonymousUser())
        work_id = self.scope['url_route']['kwargs'].get('work_id')
        self.work = await self._get_work(work_id)

        if not self.work or not await self._can_access(user, self.work):
            await self.close(code=4003)
            return

        self.group_name = f'science_publishing_chat_{self.work.id}'
        self.author_user_id = getattr(getattr(self.work, 'profile', None), 'user_id', None)
        self.editor_user_id = getattr(getattr(self.work, 'current_editor', None), 'user_id', None)
        self.chief_user_ids = await self._get_chief_user_ids()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # ожидаем {"content": "...", "metadata": {...}}
        user = self.scope.get('user', AnonymousUser())
        if not self.work or not await self._can_access(user, self.work):
            await self.close(code=4003)
            return

        text = (content.get('content') or '').strip()
        metadata = content.get('metadata') or {}
        if not text and not metadata:
            return

        message = await self._create_message(self.work, user, text, metadata)
        await self._create_receipts(message, exclude_user_ids=[getattr(user, 'id', None)])
        serialized = await self._serialize_message(message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'payload': serialized,
            },
        )
        await self._notify_participants(serialized, sender_id=getattr(user, 'id', None))

    async def chat_message(self, event):
        payload = self._stringify_uuids(event.get('payload') or {})
        await self.send_json(payload)

    @database_sync_to_async
    def _get_work(self, work_id):
        try:
            return Work.objects.select_related('profile', 'current_editor').get(pk=work_id)
        except Work.DoesNotExist:
            return None

    @database_sync_to_async
    def _can_access(self, user, work):
        return _can_access_chat_sync(user, work)

    @database_sync_to_async
    def _create_message(self, work, user, content, metadata):
        return WorkChatMessage.objects.create(
            work=work,
            author=user,
            content=content or '',
            metadata=metadata or {},
            is_system=False,
        )

    @database_sync_to_async
    def _serialize_message(self, message):
        msg = (
            WorkChatMessage.objects.select_related(
                'author',
                'author__science_publishing_profile',
            )
            .prefetch_related(
                'author__science_publishing_profile__roles',
                'receipts__recipient',
            )
            .get(pk=message.pk)
        )
        serializer = WorkChatMessageSerializer(msg)
        return serializer.data

    def _stringify_uuids(self, obj):
        if isinstance(obj, dict):
            return {k: self._stringify_uuids(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._stringify_uuids(v) for v in obj]
        # datetime -> isoformat
        from datetime import datetime
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'hex'):  # UUID
            return str(obj)
        return obj

    @database_sync_to_async
    def _create_receipts(self, message, exclude_user_ids=None):
        exclude_user_ids = set(exclude_user_ids or [])
        recipients = collect_work_user_ids(message.work)
        author_id = getattr(message.author, 'id', None)
        if author_id:
            exclude_user_ids.add(author_id)
        recipients = [uid for uid in recipients if uid and uid not in exclude_user_ids]
        if recipients:
            WorkChatReceipt.objects.bulk_create(
                [WorkChatReceipt(message=message, recipient_id=uid) for uid in recipients],
                ignore_conflicts=True,
            )
        message._prefetched_receipts = list(
            WorkChatReceipt.objects.filter(message=message).select_related('recipient')
        )
        return message._prefetched_receipts

    @database_sync_to_async
    def _get_chief_user_ids(self):
        return list(
            UserProfile.objects.filter(roles__code=EditorialRole.Code.CHIEF_EDITOR).values_list('user_id', flat=True)
        )

    async def _notify_participants(self, message_payload, sender_id=None):
        """
        Шлём короткое уведомление всем, кто связан с работой, кроме отправителя.
        """
        recipients = set()
        if self.author_user_id:
            recipients.add(self.author_user_id)
        if self.editor_user_id:
            recipients.add(self.editor_user_id)
        recipients.update([uid for uid in self.chief_user_ids if uid])

        if sender_id:
            recipients.discard(sender_id)
        if not recipients:
            return

        title = getattr(self.work, 'discipline_name', None) or getattr(self.work, 'short_description', None) or str(
            self.work.id
        )
        content = message_payload.get('content') or 'Новое сообщение в чате'

        payloads = []
        for user_id in recipients:
            route_name = 'SciencePublishingDrafts' if user_id == self.author_user_id else 'SciencePublishingTasks'
            payloads.append(
                (
                    user_id,
                    {
                        'id': str(message_payload.get('id') or f'chat-{self.work.id}-{message_payload.get("created_at")}'),
                        'type': 'chat_message',
                        'work_id': str(self.work.id),
                        'work_title': title,
                        'message': content,
                        'route_name': route_name,
                        'route_params': {},
                        'route_query': {'work': str(self.work.id), 'tab': 'chat'},
                    },
                )
            )

        if payloads:
            await self._send_notifications(payloads)

    async def _send_notifications(self, payloads):
        """
        Async версия рассылки уведомлений в персональные группы, чтобы не использовать async_to_sync.
        """
        if not payloads:
            return
        if not self.channel_layer:
            return
        for user_id, payload in payloads:
            await self.channel_layer.group_send(
                f'science_publishing_notifications_{user_id}',
                {
                    'type': 'notification.message',
                    'payload': self._stringify_uuids(payload),
                },
            )

    async def chat_receipt(self, event):
        payload = event.get('payload') or {}
        # сериализуем UUID в строку
        payload['message_ids'] = [str(mid) for mid in payload.get('message_ids', [])]
        if 'reader_id' in payload:
            payload['reader_id'] = payload['reader_id']
        if 'reader_username' in payload:
            payload['reader_username'] = str(payload['reader_username'])
        await self.send_json(self._stringify_uuids({'event': 'receipt', **payload}))


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Персональные уведомления по работам (на пользователя).
    """

    group_name: str = ''

    async def connect(self):
        user = self.scope.get('user', AnonymousUser())
        if not getattr(user, 'is_authenticated', False):
            await self.close(code=4003)
            return

        self.group_name = f'science_publishing_notifications_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._send_unread_backlog(user)

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # Сообщения от клиента не ожидаются
        return

    async def notification_message(self, event):
        payload = event.get('payload')
        if payload:
            await self.send_json(payload)

    @database_sync_to_async
    def _get_unread_receipts(self, user):
        return list(
            WorkChatReceipt.objects.filter(recipient=user, read_at__isnull=True)
            .select_related('message__work', 'message__work__profile', 'message__author')
        )

    @database_sync_to_async
    def _ensure_missing_receipts_for_user(self, user):
        """
        Создаёт квитанции для сообщений, где user является участником (автор/редактор/роль)
        и квитанции ещё нет (важно для старых сообщений).
        """
        # Работы, где пользователь автор
        from modules.science_publishing.api.models import Work, EditorialRole

        works_qs = Work.objects.filter(
            models.Q(profile__user=user) |
            models.Q(current_editor__user=user) |
            models.Q(profile__roles__code__in=[EditorialRole.Code.CHIEF_EDITOR, EditorialRole.Code.ADMINISTRATOR])
        ).distinct()

        missing_messages = WorkChatMessage.objects.filter(work__in=works_qs).exclude(
            receipts__recipient=user
        ).values_list('id', flat=True)
        WorkChatReceipt.objects.bulk_create(
            [WorkChatReceipt(message_id=mid, recipient=user) for mid in missing_messages],
            ignore_conflicts=True,
        )

    async def _send_unread_backlog(self, user):
        await self._ensure_missing_receipts_for_user(user)
        receipts = await self._get_unread_receipts(user)
        for receipt in receipts:
            msg = receipt.message
            work = getattr(msg, 'work', None)
            if not work:
                continue
            title = getattr(work, 'discipline_name', None) or getattr(work, 'short_description', None) or str(work.id)
            payload = {
                'id': str(msg.id),
                'type': 'chat_message',
                'work_id': str(work.id),
                'work_title': title,
                'author': getattr(msg.author, 'username', None),
                'message': msg.content or 'Новое сообщение в чате',
                'route_name': 'SciencePublishingDrafts' if getattr(work.profile, 'user_id', None) == user.id else 'SciencePublishingTasks',
                'route_params': {},
                'route_query': {'work': str(work.id), 'tab': 'chat'},
            }
            await self.send_json(self._stringify_uuids(payload))

    def _stringify_uuids(self, obj):
        if isinstance(obj, dict):
            return {k: self._stringify_uuids(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._stringify_uuids(v) for v in obj]
        if hasattr(obj, 'hex'):  # UUID
            return str(obj)
        return obj
