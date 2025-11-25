from datetime import datetime

from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin

from .models import EditorialRole, EditorialTask, EditorialTaskMessage, UserProfile, UserProfileRole, Work


ASSIGNABLE_WORK_STATUSES = {
    Work.Status.PENDING_CHIEF_REVIEW,
    Work.Status.IN_EDITOR_REVIEW,
    Work.Status.WAITING_FOR_AUTHOR,
    Work.Status.READY_FOR_CHIEF_APPROVAL,
}


AUTHOR_TASK_ALLOWED_STATUSES = {
    Work.Status.PENDING_CHIEF_REVIEW,
    Work.Status.IN_EDITOR_REVIEW,
    Work.Status.WAITING_FOR_AUTHOR,
    Work.Status.READY_FOR_CHIEF_APPROVAL,
}
from .serializers import (
    EditorialRoleSerializer,
    UserProfileRoleSerializer,
    UserProfileSerializer,
    WorkSerializer,
    EditorialTaskSerializer,
    EditorialTaskMessageSerializer,
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


@action(detail=True, methods=['post'], url_path='close')
def close_task(self, request, pk=None):
    """Позволяет получателю вручную закрыть задачу и оставить комментарий."""
    if self.is_swagger_fake_view():
        return Response({})
    task = self.get_object()
    if task.closed_at is not None:
        raise ValidationError({'detail': 'Задача уже закрыта.'})
    if task.recipient_id != request.user.id:
        raise PermissionDenied('Только получатель может закрыть задачу.')

    note = (request.data.get('message') or '').strip()
    task.status = EditorialTask.Status.DONE
    task.closed_at = timezone.now()
    task.updated_at = timezone.now()
    task.save(update_fields=['status', 'closed_at', 'updated_at'])
    if note:
        EditorialTaskMessage.objects.create(task=task, author=request.user, content=note, is_system=False)

    serializer = self.get_serializer(task)
    return Response(serializer.data)

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
        if not self._user_has_role(user, role_code):
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

    def _get_active_task_for_user(self, work, user):
        if not user:
            return None
        return (
            work.tasks
            .filter(recipient=user, closed_at__isnull=True)
            .order_by('-created_at')
            .first()
        )

    def _spawn_task(
        self,
        work,
        recipient,
        *,
        sender=None,
        subject=None,
        message=None,
        status=None,
        previous_task=None,
        payload=None,
        close_status=EditorialTask.Status.DONE,
        close_payload=None,
    ):
        task = EditorialTask.objects.create(
            work=work,
            recipient=recipient,
            sender=sender,
            subject=subject or 'Редакционная задача',
            message=message or '',
            status=status or EditorialTask.Status.NEW,
            previous_task=previous_task,
            payload=payload or {},
        )
        if previous_task:
            payload_to_store = previous_task.payload if close_payload is None else close_payload
            self._close_task(previous_task, status=close_status, payload=payload_to_store)
        return task

    def _close_task(self, task, *, status=None, payload=None):
        if not task:
            return
        update_fields = []
        if status and task.status != status:
            task.status = status
            update_fields.append('status')
        if payload is not None:
            task.payload = payload
            update_fields.append('payload')
        if task.closed_at is None:
            task.closed_at = timezone.now()
            update_fields.append('closed_at')
        task.updated_at = timezone.now()
        update_fields.append('updated_at')
        task.save(update_fields=update_fields)

    def _append_message(self, task, author, content='', *, metadata=None, is_system=False):
        if not content and not metadata:
            return None
        metadata = metadata or {}
        return EditorialTaskMessage.objects.create(
            task=task,
            author=author,
            content=content or '',
            metadata=metadata,
            is_system=is_system,
        )

    def _set_task_status(self, task, value):
        if task.status != value:
            task.status = value
            fields = ['status', 'updated_at']
            if value in (EditorialTask.Status.DONE, EditorialTask.Status.ARCHIVED):
                if task.closed_at is None:
                    task.closed_at = timezone.now()
                    fields.append('closed_at')
            else:
                if task.closed_at is not None:
                    task.closed_at = None
                    fields.append('closed_at')
            task.updated_at = timezone.now()
            task.save(update_fields=fields)

    def _notify_chief_editors_about_new_work(self, work, sender=None):
        title = self._work_title(work)
        message = f'Работа <{title}> поступила в рассмотрение.'
        for user in self._role_users(EditorialRole.Code.CHIEF_EDITOR):
            task = self._spawn_task(
                work,
                recipient=user,
                sender=sender,
                subject=f'Задача по работе <{title}>',
                message=message,
                status=EditorialTask.Status.NEW,
                payload={
                    'work_status': work.status,
                    'note': message,
                },
            )
            if sender:
                self._append_message(task, sender, message)

    def _get_editor_task(self, work):
        editor = getattr(work.current_editor, 'user', None)
        if not editor:
            return None
        return self._get_active_task_for_user(work, editor)

    def _get_author_task(self, work):
        author = getattr(work.profile, 'user', None)
        if not author:
            return None
        return self._get_active_task_for_user(work, author)

    def _update_chief_tasks(self, work, status_value, message=None, author=None):
        chiefs = self._role_users(EditorialRole.Code.CHIEF_EDITOR)
        if not chiefs:
            return
        for chief in chiefs:
            previous_task = self._get_active_task_for_user(work, chief)
            task = self._spawn_task(
                work,
                recipient=chief,
                sender=author,
                subject=f'Задача по работе <{self._work_title(work)}>',
                message=message,
                status=status_value,
                previous_task=previous_task,
                payload={
                    'work_status': work.status,
                    'note': message,
                },
                close_status=EditorialTask.Status.DONE,
                close_payload={
                    'work_status': work.status,
                    'note': message,
                } if message else (previous_task.payload if previous_task else None),
            )
            if message and author:
                self._append_message(task, author, message)

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

    # ------------------------------------------------------------------ #
    # updates with change logging
    # ------------------------------------------------------------------ #

    def _log_work_update(self, work, author, changes, attachments, note=''):
        """Append system messages about work updates to active tasks for author/editor so both видят историю."""
        if not changes and not attachments:
            return
        content = note or 'Обновлены данные черновика.'
        metadata = {'kind': 'work_update', 'status': work.status}
        if changes:
            metadata['changes'] = changes
        if attachments:
            metadata['attachments'] = attachments

        editor_task = self._get_editor_task(work)
        if editor_task:
            self._append_message(editor_task, author, content, metadata=metadata, is_system=True)
        author_task = self._get_author_task(work)
        if author_task and author_task != editor_task:
            self._append_message(author_task, author, content, metadata=metadata, is_system=True)

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

    @action(detail=True, methods=['post'], url_path='assign-editor')
    def assign_editor(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)
        if work.status not in ASSIGNABLE_WORK_STATUSES:
            raise ValidationError({'detail': 'Для текущего статуса работы назначение редактора недоступно.'})
        editor_profile_id = request.data.get('editor_profile')
        if not editor_profile_id:
            raise ValidationError({'editor_profile': 'Укажите редактора.'})
        try:
            editor_profile = UserProfile.objects.select_related('user').get(id=editor_profile_id)
        except UserProfile.DoesNotExist as exc:
            raise ValidationError({'editor_profile': 'Профиль не найден.'}) from exc
        if not editor_profile.roles.filter(code=EditorialRole.Code.EDITOR).exists():
            raise ValidationError({'editor_profile': 'Пользователь не имеет роли редактора.'})

        message = (request.data.get('message') or '').strip() or 'Вы назначены ответственным редактором.'
        work.current_editor = editor_profile
        work.status = Work.Status.IN_EDITOR_REVIEW
        work.save(update_fields=['current_editor', 'status', 'updated_at'])

        editor_user = editor_profile.user
        previous_task = self._get_active_task_for_user(work, request.user)
        transition_payload = {
            'work_status': work.status,
            'note': message,
            'action': 'assign_editor',
            'target_editor': editor_user.username,
        }
        task = self._spawn_task(
            work,
            recipient=editor_user,
            sender=request.user,
            subject=f'\u0417\u0430\u0434\u0430\u0447\u0430 \u043f\u043e \u0440\u0430\u0431\u043e\u0442\u0435 <{self._work_title(work)}>',
            message=message,
            status=EditorialTask.Status.IN_PROGRESS,
            previous_task=previous_task,
            payload=transition_payload,
            close_payload=transition_payload,
        )
        if message:
            self._append_message(task, request.user, message)
        display_name = editor_profile.display_name or editor_user.get_full_name() or editor_user.get_username()
        self._update_chief_tasks(
            work,
            EditorialTask.Status.IN_PROGRESS,
            message=f'Работа «{self._work_title(work)}» у редактора {display_name}.',
            author=request.user,
        )

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

        author_user = getattr(work.profile, 'user', None)
        if not author_user:
            raise ValidationError({'detail': 'У работы отсутствует автор.'})

        previous_task = self._get_active_task_for_user(work, request.user)
        task_payload = {
            'work_status': Work.Status.WAITING_FOR_AUTHOR,
            'note': message,
            'action': 'request_changes',
        }
        task = self._spawn_task(
            work,
            recipient=author_user,
            sender=request.user,
            subject=f'Запрос на работу «{self._work_title(work)}»',
            message=message,
            status=EditorialTask.Status.NEW,
            previous_task=previous_task,
            payload=task_payload,
            close_payload=task_payload,
        )
        self._append_message(
            task,
            request.user,
            message,
            metadata={
                'kind': 'request_changes',
                'status': Work.Status.WAITING_FOR_AUTHOR,
            },
        )

        work.status = Work.Status.WAITING_FOR_AUTHOR
        work.save(update_fields=['status', 'updated_at'])

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
            'status': Work.Status.IN_EDITOR_REVIEW,
        }
        if changes:
            metadata['changes'] = changes
        if attachments:
            metadata['attachments'] = attachments

        previous_task = self._get_active_task_for_user(work, request.user)
        task_payload = {
            'work_status': Work.Status.IN_EDITOR_REVIEW,
            'note': message,
            'action': 'submit_corrections',
        }
        if changes:
            task_payload['changes'] = changes
        if attachments:
            task_payload['attachments'] = attachments

        editor_task = self._spawn_task(
            work,
            recipient=editor_user,
            sender=request.user,
            subject=f'Ответ на замечания по <{self._work_title(work)}>',
            message=message,
            status=EditorialTask.Status.NEW,
            previous_task=previous_task,
            payload=task_payload,
            close_payload=task_payload,
        )
        self._append_message(
            editor_task,
            request.user,
            message,
            metadata=metadata,
        )

        work.status = Work.Status.IN_EDITOR_REVIEW
        work.save(update_fields=['status', 'updated_at'])

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

        editor_task = self._get_editor_task(work)
        if editor_task:
            payload = editor_task.payload or {}
            payload.update({
                'work_status': work.status,
                'action': 'editor_approve',
            })
            if note:
                payload['note'] = note
            self._close_task(editor_task, status=EditorialTask.Status.DONE, payload=payload)
            if note:
                self._append_message(editor_task, request.user, note)

        author_task = self._get_author_task(work)
        if author_task:
            author_payload = author_task.payload or {}
            author_payload.update({
                'work_status': work.status,
                'action': 'editor_approve',
            })
            if note:
                author_payload['note'] = note
            self._close_task(author_task, status=EditorialTask.Status.DONE, payload=author_payload)

        self._update_chief_tasks(
            work,
            EditorialTask.Status.IN_PROGRESS,
            message=f'Работа «{self._work_title(work)}» готова к утверждению.',
            author=request.user,
        )

        serializer = self.get_serializer(work)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='chief-approve')
    def chief_approve(self, request, pk=None):
        if self.is_swagger_fake_view():
            return Response({})
        work = self.get_object()
        self._ensure_user_has_role(request.user, EditorialRole.Code.CHIEF_EDITOR)
        if work.status != Work.Status.READY_FOR_CHIEF_APPROVAL:
            raise ValidationError({'detail': 'Работа еще не готова к публикации.'})

        note = (request.data.get('message') or '').strip()

        work.status = Work.Status.PUBLISHED
        work.published_at = timezone.now()
        work.save(update_fields=['status', 'published_at', 'updated_at'])

        for task in work.tasks.all():
            payload = task.payload or {}
            payload.update({'work_status': work.status, 'action': 'chief_approve'})
            if note:
                payload['note'] = note
            self._close_task(task, status=EditorialTask.Status.DONE, payload=payload)
            if note:
                self._append_message(task, request.user, note)

        serializer = self.get_serializer(work)
        return Response(serializer.data)

class EditorialTaskViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """Задачи редакционного процесса."""

    queryset = EditorialTask.objects.select_related('work', 'recipient', 'sender', 'work__profile', 'work__profile__user')
    serializer_class = EditorialTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    author_task_allowed_statuses = AUTHOR_TASK_ALLOWED_STATUSES
    filterset_fields = (
        'status',
        'recipient',
        'sender',
        'work',
        'work__profile',
        'work__publication_kind',
        'work__guideline_subtype',
        'work__training_form',
        'work__year',
    )
    search_fields = (
        'subject',
        'message',
        'work__discipline_name',
        'recipient__username',
        'work__profile__display_name',
        'work__profile__user__username',
        'work__profile__user__first_name',
        'work__profile__user__last_name',
    )
    ordering = ('-created_at',)

    # ------------------------------------------------------------------ #
    # permission helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_profile(user):
        if not getattr(user, 'is_authenticated', False):
            return None
        try:
            return user.science_publishing_profile
        except UserProfile.DoesNotExist:  # pragma: no cover - profile отсутствует
            return None

    def _user_has_role(self, user, role_code):
        profile = self._get_profile(user)
        if not profile:
            return False
        return profile.roles.filter(code=role_code).exists()

    @staticmethod
    def _parse_pk(field, raw_value):
        if raw_value in (None, ''):
            return None
        try:
            return field.to_python(raw_value)
        except (TypeError, ValueError, DjangoValidationError):
            return None

    def _assert_can_create_task(self, validated_data, sender):
        if not getattr(sender, 'is_authenticated', False):
            raise PermissionDenied('Не удалось определить пользователя.')

        work = validated_data.get('work')
        if not isinstance(work, Work):
            raise ValidationError({'work': 'Выберите корректную работу.'})

        recipient = validated_data.get('recipient')
        if recipient is None:
            raise ValidationError({'recipient': 'Укажите получателя задачи.'})

        is_privileged = sender.is_superuser or sender.is_staff or self._user_has_role(sender, EditorialRole.Code.CHIEF_EDITOR)
        if not is_privileged:
            raise PermissionDenied('Создавать задачи для авторов может только главный редактор.')

        if work.status not in self.author_task_allowed_statuses:
            raise ValidationError({'detail': 'Для текущего статуса работы нельзя создавать новые задачи автору.'})

        author_user = getattr(work.profile, 'user', None)
        if not author_user or recipient != author_user:
            raise ValidationError({'recipient': 'Задачу можно отправить только автору выбранной работы.'})

    def get_queryset(self):
        base_queryset = super().get_queryset().prefetch_related(
            'messages',
            'messages__author',
            'messages__author__science_publishing_profile',
            'messages__author__science_publishing_profile__roles',
        )
        if self.is_swagger_fake_view():
            return base_queryset.none()

        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = base_queryset
        else:
            profile = getattr(user, 'science_publishing_profile', None)
            author_work_ids = []
            if profile:
                author_work_ids = list(profile.works.values_list('id', flat=True))

            queryset = base_queryset.filter(
                models.Q(recipient=user)
                | models.Q(sender=user)
                | models.Q(work_id__in=author_work_ids)
            ).distinct()

        # Preserve queryset without activity filter for contextual lookups
        accessible_queryset = queryset

        # Show only active (open) tasks by default
        queryset = queryset.filter(closed_at__isnull=True)

        params = self.request.query_params

        target_work_id = None
        work_param = params.get('work')
        if work_param:
            target_work_id = self._parse_pk(Work._meta.pk, work_param)

        selected_task_param = params.get('selected_task')
        if target_work_id is None and selected_task_param:
            task_id = self._parse_pk(EditorialTask._meta.pk, selected_task_param)
            if task_id is not None:
                # include closed tasks when deriving context
                task = accessible_queryset.filter(pk=task_id).values('work_id').first()
                if task:
                    target_work_id = task['work_id']

        if target_work_id is not None:
            queryset = queryset.filter(work_id=target_work_id)

        author_query = params.get('author')
        if author_query:
            queryset = queryset.filter(
                models.Q(work__profile__display_name__icontains=author_query)
                | models.Q(work__profile__user__username__icontains=author_query)
                | models.Q(work__profile__user__first_name__icontains=author_query)
                | models.Q(work__profile__user__last_name__icontains=author_query)
            )

        work_title = params.get('work_title')
        if work_title:
            queryset = queryset.filter(work__discipline_name__icontains=work_title)

        subject_query = params.get('subject')
        if subject_query:
            queryset = queryset.filter(subject__icontains=subject_query)

        publication_kind = params.get('publication_kind')
        if publication_kind:
            queryset = queryset.filter(work__publication_kind=publication_kind)

        guideline_subtype = params.get('guideline_subtype')
        if guideline_subtype:
            queryset = queryset.filter(work__guideline_subtype=guideline_subtype)

        training_form = params.get('training_form')
        if training_form:
            queryset = queryset.filter(work__training_form=training_form)

        year = params.get('year')
        if year:
            try:
                queryset = queryset.filter(work__year=int(year))
            except (TypeError, ValueError):
                pass

        status_param = params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        assigned_only = params.get('assigned')
        if assigned_only and assigned_only.lower() in ('1', 'true', 'yes', 'on'):
            queryset = queryset.filter(recipient=user)

        def _parse_datetime(value):
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'):
                try:
                    return datetime.strptime(value, fmt)
                except (TypeError, ValueError):
                    continue
            return None

        created_from = _parse_datetime(params.get('created_from'))
        if created_from:
            queryset = queryset.filter(created_at__gte=created_from)

        created_to = _parse_datetime(params.get('created_to'))
        if created_to:
            queryset = queryset.filter(created_at__lte=created_to)

        updated_from = _parse_datetime(params.get('updated_from'))
        if updated_from:
            queryset = queryset.filter(updated_at__gte=updated_from)

        updated_to = _parse_datetime(params.get('updated_to'))
        if updated_to:
            queryset = queryset.filter(updated_at__lte=updated_to)

        return queryset

    def perform_create(self, serializer):
        if self.is_swagger_fake_view():
            serializer.save()
            return

        sender = self.request.user
        self._assert_can_create_task(serializer.validated_data, sender)
        serializer.save(sender=sender, status=EditorialTask.Status.NEW)

    def _can_access_task(self, task, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        if user.is_superuser or user.is_staff:
            return True
        if task.recipient_id == user.id or task.sender_id == user.id:
            return True
        author_user = getattr(task.work.profile, 'user', None)
        return author_user and author_user.id == user.id

    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        task = self.get_object()
        if request.method.lower() == 'get':
            serializer = EditorialTaskMessageSerializer(task.messages.all(), many=True)
            return Response(serializer.data)

        if self.is_swagger_fake_view():
            return Response({})

        if not self._can_access_task(task, request.user):
            raise PermissionDenied('Нет доступа к этой задаче.')

        content = (request.data.get('content') or '').strip()
        if not content:
            raise ValidationError({'content': 'Сообщение не может быть пустым.'})

        message = EditorialTaskMessage.objects.create(task=task, author=request.user, content=content)

        if task.recipient_id == request.user.id:
            updated_status = EditorialTask.Status.IN_PROGRESS
        else:
            updated_status = EditorialTask.Status.NEW
        if task.status != updated_status:
            task.status = updated_status
            task.updated_at = timezone.now()
            task.save(update_fields=['status', 'updated_at'])

        serializer = EditorialTaskMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
