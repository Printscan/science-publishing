from django.db.models.fields.files import FieldFile
from django.http import Http404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin

from .models import EditorialRole, Publication, UserProfile, UserProfileRole, Work, WorkChatMessage, WorkChatReceipt
from .serializers import (
    EditorialRoleSerializer,
    PublicationSerializer,
    UserProfileRoleSerializer,
    UserProfileSerializer,
    WorkSerializer,
    WorkChatMessageSerializer,
)
from .realtime import (
    broadcast_chat_message,
    broadcast_chat_notification,
    broadcast_editor_assignment,
    broadcast_work_published,
    collect_work_user_ids,
)


def _create_receipts_for_message(message, *, exclude_user_ids=None):
    """
    Создаёт квитанции доставки для всех участников работы (кроме автора/исключенных).
    Возвращает список созданных/существующих квитанций.
    """
    exclude_user_ids = set(u for u in (exclude_user_ids or []) if u)
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
    qs = WorkChatReceipt.objects.filter(message=message).select_related('recipient')
    receipts = list(qs)
    message._prefetched_receipts = receipts
    return receipts


def _ensure_user_receipts(messages_qs, user):
    """
    Гарантирует наличие квитанций для текущего пользователя по переданным сообщениям.
    Нужно для старых сообщений, созданных до появления WorkChatReceipt.
    """
    if not getattr(user, 'is_authenticated', False):
        return
    message_ids = list(
        messages_qs.exclude(receipts__recipient=user)
        .values_list('id', flat=True)
    )
    if not message_ids:
        return
    WorkChatReceipt.objects.bulk_create(
        [WorkChatReceipt(message_id=mid, recipient=user) for mid in message_ids],
        ignore_conflicts=True,
    )


class EditorialRoleViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """CRUD операции над справочником ролей."""

    queryset = EditorialRole.objects.all()
    serializer_class = EditorialRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('code',)
    search_fields = ('name', 'code')
    ordering = ('name',)


class UserProfileViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """Работа с профилями пользователей научных публикаций."""

    queryset = UserProfile.objects.select_related('user').prefetch_related('roles', 'works')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = (
        'is_active',
        'roles__code',
        'organization',
        'department',
        'position',
    )
    search_fields = (
        'display_name',
        'user__username',
        'user__first_name',
        'user__last_name',
        'organization',
    )
    ordering = ('user__last_name', 'user__first_name')

    def get_queryset(self):
        base_queryset = super().get_queryset()
        return self.get_safe_queryset(base_queryset)

    def _get_or_create_profile(self, user):
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'display_name': user.get_full_name() or user.username},
        )
        return profile

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """Получение и обновление собственного профиля."""
        if self.is_swagger_fake_view():
            return Response({})

        profile = self._get_or_create_profile(request.user)

        if request.method.lower() == 'patch':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class UserProfileRoleViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """Назначения ролей пользователям."""

    queryset = UserProfileRole.objects.select_related('profile', 'profile__user', 'role', 'assigned_by')
    serializer_class = UserProfileRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('role__code', 'profile__id')
    search_fields = ('role__name', 'profile__display_name', 'profile__user__username')
    ordering = ('profile__user__last_name', 'role__name')

    def get_queryset(self):
        base_queryset = super().get_queryset()
        return self.get_safe_queryset(base_queryset)

    def perform_create(self, serializer):
        assigned_by = None if self.is_swagger_fake_view() else self.request.user
        serializer.save(assigned_by=assigned_by)


class WorkViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """Работы и редакционный процесс."""

    CORRECTION_MUTABLE_FIELDS = (
        'rector_name',
        'pages_count',
        'year',
        'udc',
        'discipline_name',
        'bbk',
        'discipline_topic',
        'developers',
        'publication_kind',
        'guideline_subtype',
        'training_form',
        'scientific_editor',
        'computer_layout',
        'author_full_name',
        'co_authors',
        'faculty',
        'department',
        'short_description',
    )
    CORRECTION_FILE_FIELDS = ('document',)


    queryset = Work.objects.select_related('profile', 'profile__user', 'current_editor', 'current_editor__user')
    serializer_class = WorkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = (
        'profile',
        'publication_kind',
        'guideline_subtype',
        'training_form',
        'year',
        'status',
    )
    search_fields = (
        'discipline_name',
        'discipline_topic',
        'author_full_name',
        'co_authors',
        'profile__display_name',
    )
    ordering = ('-year', 'discipline_name')

    # --------------------------------------------------------------------- #
    # helpers
    # --------------------------------------------------------------------- #

    def get_queryset(self):
        base_queryset = super().get_queryset()
        if self.is_swagger_fake_view():
            return base_queryset.none()
        queryset = base_queryset
        user = self.request.user
        if not self._is_privileged_user(user):
            queryset = queryset.filter(profile__user=user)
        return self.get_safe_queryset(queryset)

    def _get_existing_profile(self, user):
        if not getattr(user, 'is_authenticated', False):
            return None
        try:
            return user.science_publishing_profile
        except UserProfile.DoesNotExist:
            return None

    def _get_profile_for_request(self):
        if self.is_swagger_fake_view():
            return None
        profile = self._get_existing_profile(self.request.user)
        if profile:
            return profile
        return UserProfile.objects.create(
            user=self.request.user,
            display_name=self.request.user.get_full_name() or self.request.user.username,
        )

    def _user_has_role(self, user, role_code):
        profile = self._get_existing_profile(user)
        if not profile:
            return False
        return profile.roles.filter(code=role_code).exists()

    def _ensure_user_has_role(self, user, role_code):
        """
        Проверяет наличие нужной роли у пользователя.
        Администраторов считаем эквивалентными главному редактору для действий с работами.
        """
        codes = {role_code} if isinstance(role_code, str) else set(role_code)
        # Администратор может выполнять действия главреда (назначать, публиковать).
        if EditorialRole.Code.CHIEF_EDITOR in codes:
            codes.add(EditorialRole.Code.ADMINISTRATOR)

        if not any(self._user_has_role(user, code) for code in codes):
            raise PermissionDenied('Недостаточно прав для выполнения действия.')

    def _is_privileged_user(self, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        if user.is_superuser or user.is_staff:
            return True
        return any(
            self._user_has_role(user, code)
            for code in (
                EditorialRole.Code.ADMINISTRATOR,
                EditorialRole.Code.CHIEF_EDITOR,
                EditorialRole.Code.EDITOR,
            )
        )

    def _role_users(self, role_code):
        assignments = (
            UserProfileRole.objects
            .select_related('profile__user')
            .filter(role__code=role_code)
        )
        users = []
        seen = set()
        for assignment in assignments:
            user = getattr(assignment.profile, 'user', None)
            if not user or user.id in seen:
                continue
            seen.add(user.id)
            users.append(user)
        return users

    def _work_title(self, work):
        return work.discipline_name or work.get_publication_kind_display() or str(work.id)

    @staticmethod
    def _get_work_or_404(pk):
        # прямой поиск по работе
        work = Work.objects.filter(pk=pk).first()
        if work:
            return work
        # поиск по публикации (id публикации или ссылка на исходную работу)
        publication = Publication.objects.filter(pk=pk).first()
        if publication and publication.source_work:
            return publication.source_work
        publication_by_source = Publication.objects.filter(source_work_id=pk).first()
        if publication_by_source and publication_by_source.source_work:
            return publication_by_source.source_work
        raise Http404('Работа не найдена.')

    @staticmethod
    def _sync_publication_from_work(work):
        """Создает или обновляет публикацию на основании работы."""
        if not work:
            return None
        defaults = {
            'profile': work.profile,
            'author_full_name': work.author_full_name,
            'publication_kind': work.publication_kind,
            'guideline_subtype': work.guideline_subtype,
            'discipline_name': work.discipline_name,
            'discipline_topic': work.discipline_topic,
            'rector_name': work.rector_name,
            'year': work.year,
            'pages_count': work.pages_count,
            'udc': work.udc,
            'bbk': work.bbk,
            'developers': work.developers,
            'scientific_editor': work.scientific_editor,
            'computer_layout': work.computer_layout,
            'co_authors': work.co_authors,
            'training_form': work.training_form,
            'faculty': work.faculty,
            'department': work.department,
            'short_description': work.short_description,
            'document': work.document,
            'status': Work.Status.PUBLISHED,
            'current_editor': work.current_editor,
            'published_at': work.published_at,
        }
        publication, _ = Publication.objects.update_or_create(
            source_work=work,
            defaults=defaults,
        )
        return publication

    @staticmethod
    def _finalize_publication_and_remove_work(work, note=None, actor=None):
        """
        Создаёт публикацию, при необходимости записывает финальное сообщение и удаляет исходную работу.
        Возвращает объект публикации.
        """
        publication = WorkViewSet._sync_publication_from_work(work)
        # каскадно удалит переписку/чаты/файлы черновика
        work.delete()
        return publication

    def _can_access_chat(self, user, work):
        if not getattr(user, 'is_authenticated', False):
            return False
        if user.is_superuser or user.is_staff:
            return True
        if getattr(work.profile, 'user', None) == user:
            return True
        if getattr(getattr(work, 'current_editor', None), 'user', None) == user:
            return True
        return self._user_has_role(user, EditorialRole.Code.CHIEF_EDITOR) or self._user_has_role(
            user, EditorialRole.Code.ADMINISTRATOR
        )

    @staticmethod
    def _append_chat_message(work, author, content='', *, metadata=None, is_system=False):
        if not author:
            return None
        if not content and not metadata:
            return None
        message = WorkChatMessage.objects.create(
            work=work,
            author=author,
            content=content or '',
            metadata=metadata or {},
            is_system=is_system,
        )
        _create_receipts_for_message(message, exclude_user_ids=[getattr(author, 'id', None)])
        broadcast_chat_message(message)
        broadcast_chat_notification(message, skip_user_ids=[getattr(author, 'id', None)])
        return message

    def _notify_chief_editors_about_new_work(self, work, sender=None, message=None):
        title = self._work_title(work)
        note = message or f'Работа <{title}> поступила в рассмотрение.'
        for user in self._role_users(EditorialRole.Code.CHIEF_EDITOR):
            author = sender or user
            self._append_chat_message(
                work,
                author,
                note,
                metadata={
                    'work_status': work.status,
                    'kind': 'notification',
                    'recipient': 'chief_editor',
                },
                is_system=sender is None,
            )

    def _extract_correction_payload(self, request):
        payload = {}
        data = request.data
        files = request.FILES

        for field in self.CORRECTION_MUTABLE_FIELDS:
            if field in data:
                payload[field] = data.get(field)

        for field in self.CORRECTION_FILE_FIELDS:
            if field in files:
                payload[field] = files.get(field)

        return payload

    def _collect_work_changes(self, work, validated_data):
        changes = []
        for field, new_value in validated_data.items():
            field_label = self._get_field_label(work, field)
            old_value = getattr(work, field)

            if field in self.CORRECTION_FILE_FIELDS:
                old_display = self._format_file_value(old_value)
                new_display = self._format_file_value(new_value)
            else:
                old_display = self._format_field_value(field, old_value, work)
                new_display = self._format_field_value(field, new_value, work)

            if old_display == new_display:
                continue

            changes.append(
                {
                    'field': field,
                    'label': field_label,
                    'old': old_display,
                    'new': new_display,
                }
            )
        return changes

    def _collect_work_attachments(self, work, validated_data, request=None):
        attachments = []
        for field in self.CORRECTION_FILE_FIELDS:
            if field not in validated_data:
                continue
            file_value = getattr(work, field, None)
            if not file_value:
                continue
            attachment = {
                'field': field,
                'label': self._get_field_label(work, field),
                'name': file_value.name.split('/')[-1],
                'url': file_value.url if hasattr(file_value, 'url') else None,
            }
            if attachment['url'] and request is not None:
                try:
                    attachment['absolute_url'] = request.build_absolute_uri(attachment['url'])
                except Exception:
                    attachment['absolute_url'] = attachment['url']
            attachments.append(attachment)
        return attachments

    @staticmethod
    def _get_field_label(instance, field_name):
        field = instance._meta.get_field(field_name)
        return str(getattr(field, 'verbose_name', field.name)).capitalize()

    @staticmethod
    def _format_field_value(field_name, value, instance):
        if value is None:
            return ''
        field = instance._meta.get_field(field_name)
        if hasattr(field, 'choices') and field.choices:
            display_map = dict(field.flatchoices)
            return display_map.get(value, value)
        if isinstance(value, FieldFile) or hasattr(value, 'name') and not isinstance(value, str):
            return WorkViewSet._format_file_value(value)
        if isinstance(value, (int, float)):
            return value
        return str(value)

    @staticmethod
    def _format_file_value(value):
        if not value:
            return ''
        name = getattr(value, 'name', None)
        if not name:
            return ''
        return name.split('/')[-1]

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #

    def perform_create(self, serializer):
        profile = serializer.validated_data.get('profile') or self._get_profile_for_request()
        required_fields = [
            'rector_name',
            'pages_count',
            'year',
            'udc',
            'discipline_name',
            'bbk',
            'discipline_topic',
            'developers',
            'publication_kind',
            'guideline_subtype',
            'training_form',
            'scientific_editor',
            'computer_layout',
            'author_full_name',
            'co_authors',
            'faculty',
            'department',
        ]
        missing = []
        data = self.request.data
        publication_kind = data.get('publication_kind')
        for field in required_fields:
            if field == 'guideline_subtype' and publication_kind != Work.PublicationKind.METHOD_GUIDELINES:
                continue
            value = data.get(field)
            if value is None or str(value).strip() == '':
                missing.append(field)
        if 'document' not in self.request.FILES:
            missing.append('document')
        if missing:
            raise ValidationError({field: 'Поле обязательно для заполнения.' for field in missing})

        work = serializer.save(
            profile=profile,
            status=Work.Status.DRAFT,
            current_editor=None,
            published_at=None,
        )
        if not self.is_swagger_fake_view() and work.status != Work.Status.DRAFT:
            sender = self.request.user if self.request.user.is_authenticated else None
            self._notify_chief_editors_about_new_work(work, sender=sender)

    def destroy(self, request, *args, **kwargs):
        work = self.get_object()

        if self.is_swagger_fake_view():
            return Response(status=status.HTTP_204_NO_CONTENT)

        if self._is_privileged_user(request.user):
            self.perform_destroy(work)
            return Response(status=status.HTTP_204_NO_CONTENT)

        author_user = getattr(getattr(work, 'profile', None), 'user', None)
        if not author_user or author_user.id != request.user.id:
            raise PermissionDenied('Удалять черновик может только автор.')

        if work.status != Work.Status.DRAFT:
            raise ValidationError({'detail': 'Удалить можно только черновик.'})

        self.perform_destroy(work)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='force-publish')
    def force_publish(self, request, pk=None):
        """Публикация работы в любом статусе (для главреда)."""
        if self.is_swagger_fake_view():
            return Response({})
        work = self._get_work_or_404(pk)
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)

        note = (request.data.get('message') or '').strip()

        work.status = Work.Status.PUBLISHED
        work.published_at = timezone.now()
        work.save(update_fields=['status', 'published_at', 'updated_at'])

        # запишем в чат итоговое сообщение
        can_chat = False
        if getattr(request.user, 'is_authenticated', False):
            if request.user.is_superuser or request.user.is_staff:
                can_chat = True
            else:
                author_user = getattr(work.profile, 'user', None)
                editor_user = getattr(getattr(work, 'current_editor', None), 'user', None)
                can_chat = request.user in (author_user, editor_user)
                if not can_chat:
                    try:
                        profile = request.user.science_publishing_profile
                        can_chat = profile.roles.filter(
                            code__in=[EditorialRole.Code.ADMINISTRATOR, EditorialRole.Code.CHIEF_EDITOR]
                        ).exists()
                    except UserProfile.DoesNotExist:
                        can_chat = False
        if can_chat:
            WorkChatMessage.objects.create(
                work=work,
                author=request.user,
                content=note or 'Работа опубликована принудительно.',
                metadata={
                    'action': 'force_publish',
                    'work_status': work.status,
                },
                is_system=False,
            )

        broadcast_work_published(work, note=note or 'Работа опубликована.')
        publication = self._finalize_publication_and_remove_work(work, note=note, actor=request.user)
        serializer = PublicationSerializer(publication, context={'request': request})
        return Response(serializer.data)

    # ------------------------------------------------------------------ #
    # updates with change logging
    # ------------------------------------------------------------------ #

    def _log_work_update(self, work, author, changes, attachments, note=''):
        """Добавляет запись в чат о правках в работе."""
        if not changes and not attachments:
            return
        content = note or 'Обновлены данные черновика.'
        metadata = {'kind': 'work_update', 'status': work.status}
        if changes:
            metadata['changes'] = changes
        if attachments:
            metadata['attachments'] = attachments

        if self._can_access_chat(author, work):
            self._append_chat_message(work, author, content, metadata=metadata, is_system=False)

    def _update_with_changes(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        changes = self._collect_work_changes(instance, serializer.validated_data)
        attachments = self._collect_work_attachments(instance, serializer.validated_data, request=request)
        self.perform_update(serializer)
        instance.refresh_from_db()

        note = (request.data.get('message') or '').strip()
        self._log_work_update(instance, request.user, changes, attachments, note=note)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return self._update_with_changes(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self._update_with_changes(request, *args, **kwargs)

    # ------------------------------------------------------------------ #
    # custom endpoints
    # ------------------------------------------------------------------ #

    @action(detail=False, methods=['get'], url_path='my')
    def my_works(self, request):
        """Работы текущего пользователя."""
        if self.is_swagger_fake_view():
            return Response([])

        profile = self._get_profile_for_request()
        queryset = (
            super()
            .get_queryset()
            .filter(profile=profile)
            .order_by('-created_at')
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my/drafts')
    def my_drafts(self, request):
        """Черновики текущего пользователя (все статусы, кроме опубликованных)."""
        if self.is_swagger_fake_view():
            return Response([])

        profile = self._get_profile_for_request()
        queryset = (
            super()
            .get_queryset()
            .filter(profile=profile)
            .exclude(status=Work.Status.PUBLISHED)
            .order_by('-created_at')
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my/published')
    def my_published(self, request):
        """Опубликованные работы текущего пользователя."""
        if self.is_swagger_fake_view():
            return Response([])

        profile = self._get_profile_for_request()
        queryset = (
            super()
            .get_queryset()
            .filter(profile=profile, status=Work.Status.PUBLISHED)
            .order_by('-published_at', '-created_at')
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='chat')
    def chat(self, request, pk=None):
        """Простой чат между участниками по конкретной работе."""
        work = self.get_object()
        if self.is_swagger_fake_view():
            return Response([] if request.method.lower() == 'get' else {})
        if not self._can_access_chat(request.user, work):
            raise PermissionDenied('Недостаточно прав для просмотра переписки.')

        if request.method.lower() == 'get':
            messages = (
                WorkChatMessage.objects.filter(work=work)
                .select_related('author', 'author__science_publishing_profile')
                .prefetch_related('author__science_publishing_profile__roles', 'receipts__recipient')
                .order_by('created_at')
            )
            _ensure_user_receipts(messages, request.user)
            serializer = WorkChatMessageSerializer(messages, many=True, context={'request': request})
            return Response(serializer.data)

        content = (request.data.get('content') or '').strip()
        metadata = request.data.get('metadata') or {}
        if not content and not metadata:
            raise ValidationError({'content': 'Сообщение не может быть пустым.'})
        if not isinstance(metadata, dict):
            metadata = {}
        message = WorkChatMessage.objects.create(
            work=work,
            author=request.user,
            content=content,
            metadata=metadata,
            is_system=False,
        )
        broadcast_chat_message(message)
        _create_receipts_for_message(message, exclude_user_ids=[request.user.id if request.user.is_authenticated else None])
        broadcast_chat_notification(message, skip_user_ids=[request.user.id if request.user.is_authenticated else None])
        serializer = WorkChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='chat/mark-read')
    def mark_chat_read(self, request, pk=None):
        """Помечает сообщения по работе как прочитанные текущим пользователем."""
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        if not self._can_access_chat(request.user, work):
            raise PermissionDenied('Недостаточно прав для переписки.')

        ids = request.data.get('message_ids') or request.data.get('ids') or []
        if not isinstance(ids, (list, tuple)):
            raise ValidationError({'message_ids': 'Ожидается список идентификаторов.'})
        ids = [str(i) for i in ids if i]
        if not ids:
            return Response({'updated': 0})

        # гарантируем, что квитанции существуют (важно для старых сообщений)
        missing_ids = WorkChatMessage.objects.filter(work=work, id__in=ids).exclude(
            receipts__recipient=request.user
        ).values_list('id', flat=True)
        WorkChatReceipt.objects.bulk_create(
            [WorkChatReceipt(message_id=mid, recipient=request.user) for mid in missing_ids],
            ignore_conflicts=True,
        )

        receipts_qs = WorkChatReceipt.objects.filter(message__work=work, recipient=request.user, message_id__in=ids)
        updated = receipts_qs.filter(read_at__isnull=True).update(read_at=timezone.now())
        if updated:
            # сообщаем в чат-канал о прочтении
            read_at = timezone.now().isoformat()
            payload = {
                'message_ids': ids,
                'reader_id': request.user.id,
                'reader_username': request.user.username,
                'read_at': read_at,
            }
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.group_send)(
                    f'science_publishing_chat_{work.id}',
                    {
                        'type': 'chat.receipt',
                        'payload': payload,
                    },
                )
        return Response({'updated': updated})

    @action(detail=True, methods=['post'], url_path='chat/mark-read-up-to')
    def mark_chat_read_up_to(self, request, pk=None):
        """
        Помечает как прочитанные все сообщения по работе до указанного message_id (включительно).
        Удобно для front, когда видна часть ленты и нужно прочитать одним вызовом.
        """
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        if not self._can_access_chat(request.user, work):
            raise PermissionDenied('Недостаточно прав для переписки.')

        message_id = request.data.get('message_id') or request.data.get('last_id')
        if not message_id:
            raise ValidationError({'message_id': 'Обязательное поле.'})

        # Игнорируем временные client-id (pending), чтобы не падать по UUID
        try:
            anchor = WorkChatMessage.objects.get(work=work, id=message_id)
        except (WorkChatMessage.DoesNotExist, ValueError, ValidationError):
            return Response({'updated': 0, 'skipped': True})

        # Найдём все сообщения до него по времени; на случай одинаковых created_at включаем id.
        target_ids = list(
            WorkChatMessage.objects.filter(
                work=work,
                created_at__lt=anchor.created_at,
            ).values_list('id', flat=True)
        )
        target_ids.append(str(anchor.id))
        if not target_ids:
            return Response({'updated': 0})

        missing_ids = WorkChatMessage.objects.filter(work=work, id__in=target_ids).exclude(
            receipts__recipient=request.user
        ).values_list('id', flat=True)
        WorkChatReceipt.objects.bulk_create(
            [WorkChatReceipt(message_id=mid, recipient=request.user) for mid in missing_ids],
            ignore_conflicts=True,
        )

        receipts_qs = WorkChatReceipt.objects.filter(message__work=work, recipient=request.user, message_id__in=target_ids)
        updated = receipts_qs.filter(read_at__isnull=True).update(read_at=timezone.now())
        if updated:
            read_at = timezone.now().isoformat()
            payload = {
                'message_ids': [str(tid) for tid in target_ids],
                'reader_id': request.user.id,
                'reader_username': request.user.username,
                'read_at': read_at,
            }
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            layer = get_channel_layer()
            if layer:
                async_to_sync(layer.group_send)(
                    f'science_publishing_chat_{work.id}',
                    {
                        'type': 'chat.receipt',
                        'payload': payload,
                    },
                )

        return Response({'updated': updated, 'message_ids': target_ids})

    @action(detail=True, methods=['post'], url_path='assign-editor')
    def assign_editor(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)
        editor_profile_id = request.data.get('editor_profile')
        if not editor_profile_id:
            raise ValidationError({'editor_profile': 'Укажите редактора.'})
        try:
            editor_profile = UserProfile.objects.select_related('user').get(id=editor_profile_id)
        except UserProfile.DoesNotExist as exc:
            raise ValidationError({'editor_profile': 'Профиль не найден.'}) from exc
        if not editor_profile.roles.filter(code=EditorialRole.Code.EDITOR).exists():
            raise ValidationError({'editor_profile': 'Пользователь не имеет роли редактора.'})
        # Не позволяем назначать редактором автора работы
        author_user = getattr(work.profile, 'user', None)
        if author_user and editor_profile.user_id == author_user.id:
            raise ValidationError({'editor_profile': 'Нельзя назначать автора редактором собственной работы.'})

        message = (request.data.get('message') or '').strip()
        previous_editor = work.current_editor
        work.current_editor = editor_profile
        work.status = Work.Status.IN_EDITOR_REVIEW
        work.save(update_fields=['current_editor', 'status', 'updated_at'])

        editor_user = editor_profile.user
        display_name = editor_profile.display_name or editor_user.get_full_name() or editor_user.get_username()

        metadata = {
            'action': 'assign_editor',
            'work_status': work.status,
            'editor': display_name,
            'editor_username': editor_user.get_username(),
        }
        if previous_editor and previous_editor != editor_profile:
            prev_user = previous_editor.user
            metadata['previous_editor'] = prev_user.get_username()
        default_note = f'Назначен редактор: {display_name}.'
        if self._can_access_chat(request.user, work):
            self._append_chat_message(
                work,
                request.user,
                message or default_note,
                metadata=metadata,
            )
        broadcast_editor_assignment(work, editor_profile, note=message or default_note)

        serializer = self.get_serializer(work)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='request-changes')
    def request_changes(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        editor_profile = work.current_editor
        if not editor_profile or editor_profile.user_id != request.user.id:
            raise PermissionDenied('Вы не являетесь назначенным редактором.')
        if work.status != Work.Status.IN_EDITOR_REVIEW:
            raise ValidationError({'detail': 'Запросить исправления можно только пока работа в редакторе.'})

        message = (request.data.get('message') or '').strip()
        if not message:
            raise ValidationError({'message': 'Пожалуйста, заполните комментарий к запросу.'})

        work.status = Work.Status.WAITING_FOR_AUTHOR
        work.save(update_fields=['status', 'updated_at'])
        if self._can_access_chat(request.user, work):
            self._append_chat_message(
                work,
                request.user,
                message,
                metadata={
                    'kind': 'request_changes',
                    'action': 'request_changes',
                    'work_status': work.status,
                },
            )

        serializer = self.get_serializer(work)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='submit-corrections')
    @action(detail=True, methods=['post'], url_path='submit-corrections')
    def submit_corrections(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        author_user = getattr(work.profile, 'user', None)
        if not author_user or author_user.id != request.user.id:
            raise PermissionDenied('Автор не может изменять чужую работу.')

        awaiting_author = work.status == Work.Status.WAITING_FOR_AUTHOR
        if awaiting_author and (not work.current_editor or not getattr(work.current_editor, 'user', None)):
            raise ValidationError({'detail': 'У работы не назначен редактор.'})

        message = (request.data.get('message') or '').strip()
        if awaiting_author and not message:
            raise ValidationError({'message': 'Комментарий обязателен для ответа редактору.'})

        update_payload = self._extract_correction_payload(request)
        if not update_payload:
            raise ValidationError({'detail': 'В запросе не переданы данные для обновления.'})

        serializer = self.get_serializer(work, data=update_payload, partial=True)
        serializer.is_valid(raise_exception=True)
        changes = self._collect_work_changes(work, serializer.validated_data)
        serializer.save()

        if not awaiting_author:
            refreshed = self.get_serializer(work)
            return Response(refreshed.data)

        attachments = self._collect_work_attachments(work, serializer.validated_data, request=request)

        editor_user = work.current_editor.user
        metadata = {
            'kind': 'correction',
            'action': 'submit_corrections',
            'status': Work.Status.IN_EDITOR_REVIEW,
            'work_status': Work.Status.IN_EDITOR_REVIEW,
        }
        if changes:
            metadata['changes'] = changes
        if attachments:
            metadata['attachments'] = attachments

        work.status = Work.Status.IN_EDITOR_REVIEW
        work.save(update_fields=['status', 'updated_at'])
        if self._can_access_chat(request.user, work):
            self._append_chat_message(
                work,
                request.user,
                message,
                metadata=metadata,
            )

        serializer = self.get_serializer(work)
        return Response(serializer.data)
    @action(detail=True, methods=['post'], url_path='editor-approve')
    def editor_approve(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        editor_profile = work.current_editor
        if not editor_profile or editor_profile.user_id != request.user.id:
            raise PermissionDenied('Вы не являетесь назначенным редактором.')
        if work.status not in (Work.Status.IN_EDITOR_REVIEW, Work.Status.WAITING_FOR_AUTHOR):
            raise ValidationError({'detail': 'Работа пока не готова к отправке главному редактору.'})

        note = (request.data.get('message') or '').strip()

        work.status = Work.Status.READY_FOR_CHIEF_APPROVAL
        work.save(update_fields=['status', 'updated_at'])
        if self._can_access_chat(request.user, work):
            self._append_chat_message(
                work,
                request.user,
                note or 'Работа отправлена главному редактору.',
                metadata={
                    'action': 'editor_approve',
                    'work_status': work.status,
                },
            )

        serializer = self.get_serializer(work)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='chief-approve')
    def chief_approve(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self._get_work_or_404(pk)
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)
        if work.status != Work.Status.READY_FOR_CHIEF_APPROVAL:
            raise ValidationError({'detail': 'Работа еще не готова к публикации.'})

        note = (request.data.get('message') or '').strip()

        work.status = Work.Status.PUBLISHED
        work.published_at = timezone.now()
        work.save(update_fields=['status', 'published_at', 'updated_at'])
        if self._can_access_chat(request.user, work):
            self._append_chat_message(
                work,
                request.user,
                note or 'Главный редактор утвердил публикацию.',
                metadata={
                    'action': 'chief_approve',
                    'work_status': work.status,
                },
            )

        broadcast_work_published(work, note=note or 'Работа опубликована.')
        publication = self._finalize_publication_and_remove_work(work, note=note, actor=request.user)
        serializer = PublicationSerializer(publication, context={'request': request})
        return Response(serializer.data)


class PublicationViewSet(SwaggerSafeMixin, viewsets.ReadOnlyModelViewSet):
    """Публикации (отдельная таблица после утверждения работы)."""

    queryset = Publication.objects.select_related(
        'profile',
        'profile__user',
        'current_editor',
        'current_editor__user',
        'source_work',
    )
    serializer_class = PublicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = (
        'profile',
        'publication_kind',
        'guideline_subtype',
        'training_form',
        'year',
    )
    search_fields = (
        'discipline_name',
        'discipline_topic',
        'author_full_name',
        'co_authors',
        'profile__display_name',
        'profile__user__username',
    )
    ordering = ('-published_at', '-created_at')

    def get_queryset(self):
        base_queryset = super().get_queryset()
        if self.is_swagger_fake_view():
            return base_queryset.none()
        # Для опубликованных работ показываем весь каталог всем авторизованным пользователям.
        return self.get_safe_queryset(base_queryset)

    @action(detail=True, methods=['post'], url_path='force-publish')
    def force_publish(self, request, pk=None):
        """Публикация работы в любом статусе (для главреда)."""
        if self.is_swagger_fake_view():
            return Response({})
        work = self._get_work_or_404(pk)
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)

        note = (request.data.get('message') or '').strip()

        work.status = Work.Status.PUBLISHED
        work.published_at = timezone.now()
        work.save(update_fields=['status', 'published_at', 'updated_at'])
        author_user = getattr(work.profile, 'user', None)
        editor_user = getattr(getattr(work, 'current_editor', None), 'user', None)
        if getattr(request.user, 'is_authenticated', False):
            can_chat = False
            if request.user.is_superuser or request.user.is_staff:
                can_chat = True
            elif request.user == author_user or request.user == editor_user:
                can_chat = True
            else:
                try:
                    profile = request.user.science_publishing_profile
                    can_chat = profile.roles.filter(
                        code__in=[EditorialRole.Code.ADMINISTRATOR, EditorialRole.Code.CHIEF_EDITOR]
                    ).exists()
                except UserProfile.DoesNotExist:
                    can_chat = False
        else:
            can_chat = False
        if can_chat:
            WorkChatMessage.objects.create(
                work=work,
                author=request.user,
                content=note or 'Работа опубликована принудительно.',
                metadata={
                    'action': 'force_publish',
                    'work_status': work.status,
                },
                is_system=False,
            )

        broadcast_work_published(work, note=note or 'Работа опубликована.')
        self._sync_publication_from_work(work)

        serializer = self.get_serializer(work)
        return Response(serializer.data)
