from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.modules.science_publishing.models import (
    EditorialRole,
    UserProfile,
    UserProfileRole,
    Work,
    EditorialTask,
)
from django.utils import timezone


class SciencePublishingFlowTests(APITestCase):
    """Проверяет полный круг публикации от черновика до утверждения."""
    base_path = '/api/science_publishing'

    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            username='test_author',
            email='author@example.com',
            password='author_pass',
        )
        self.editor = User.objects.create_user(
            username='test_editor',
            email='editor@example.com',
            password='editor_pass',
        )
        self.chief = User.objects.create_user(
            username='test_chief',
            email='chief@example.com',
            password='chief_pass',
        )

        self.author_profile = UserProfile.objects.create(user=self.author, display_name='Author Test')
        self.editor_profile = UserProfile.objects.create(user=self.editor, display_name='Editor Test')
        self.chief_profile = UserProfile.objects.create(user=self.chief, display_name='Chief Test')

        self._assign_role(self.author_profile, EditorialRole.Code.AUTHOR, 'Автор')
        self._assign_role(self.editor_profile, EditorialRole.Code.EDITOR, 'Редактор')
        self._assign_role(self.chief_profile, EditorialRole.Code.CHIEF_EDITOR, 'Главный редактор')

    @staticmethod
    def _assign_role(profile, code, default_name):
        role, _ = EditorialRole.objects.get_or_create(code=code, defaults={'name': default_name})
        UserProfileRole.objects.get_or_create(profile=profile, role=role)

    @staticmethod
    def _extract_results(payload):
        if isinstance(payload, dict):
            return payload.get('results', [])
        return payload

    def _create_work(self):
        payload = {
            'discipline_name': 'Тестовая работа',
            'discipline_topic': 'Новый учебник',
            'publication_kind': 'method_guidelines',
            'training_form': 'full_time',
            'year': 2026,
            'author_full_name': 'Author Test',
        }
        self.client.force_authenticate(self.author)
        response = self.client.post(f'{self.base_path}/works/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        work = Work.objects.get(id=response.json()['id'])
        # Автор отправляет работу главреду (меняем статус на pending)
        work.status = Work.Status.PENDING_CHIEF_REVIEW
        work.save(update_fields=['status'])
        return work

    def test_full_publication_cycle(self):
        work = self._create_work()

        # Задача создаётся автоматически у главного редактора
        chief_tasks = EditorialTask.objects.filter(work=work, recipient=self.chief)
        self.assertEqual(chief_tasks.count(), 1)

        # Главред назначает редактора
        self.client.force_authenticate(self.chief)
        assign_payload = {'editor_profile': str(self.editor_profile.id), 'message': 'Пожалуйста, возьми работу.'}
        assign_url = f'{self.base_path}/works/{work.id}/assign-editor/'
        response = self.client.post(assign_url, assign_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        work.refresh_from_db()
        self.assertEqual(work.status, Work.Status.IN_EDITOR_REVIEW)
        self.assertEqual(work.current_editor_id, self.editor_profile.id)

        # Редактор отправляет работу главреду
        self.client.force_authenticate(self.editor)
        editor_approve_url = f'{self.base_path}/works/{work.id}/editor-approve/'
        response = self.client.post(editor_approve_url, {'message': 'Готово для подтверждения'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        work.refresh_from_db()
        self.assertEqual(work.status, Work.Status.READY_FOR_CHIEF_APPROVAL)

        # Главред утверждает публикацию
        self.client.force_authenticate(self.chief)
        chief_approve_url = f'{self.base_path}/works/{work.id}/chief-approve/'
        response = self.client.post(chief_approve_url, {'message': 'Утверждаю'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        work.refresh_from_db()
        self.assertEqual(work.status, Work.Status.PUBLISHED)

    def test_tasks_scope_per_user(self):
        work = self._create_work()

        # Главред видит задачу
        self.client.force_authenticate(self.chief)
        resp = self.client.get(f'{self.base_path}/tasks/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        chief_tasks = self._extract_results(resp.json())
        self.assertTrue(any(item['work'] == str(work.id) for item in chief_tasks))

        # Автор видит только свои задачи (по своим работам)
        self.client.force_authenticate(self.author)
        resp = self.client.get(f'{self.base_path}/tasks/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = self._extract_results(resp.json())
        self.assertTrue(any(item['work'] == str(work.id) for item in data))

    def test_tasks_filtered_by_selected_task_even_when_closed(self):
        work_primary = self._create_work()
        work_secondary = self._create_work()

        open_task_primary = EditorialTask.objects.create(
            work=work_primary,
            recipient=self.chief,
            sender=self.author,
            subject='Primary open task',
            status=EditorialTask.Status.NEW,
        )
        closed_task_primary = EditorialTask.objects.create(
            work=work_primary,
            recipient=self.chief,
            sender=self.author,
            subject='Primary closed task',
            status=EditorialTask.Status.DONE,
            closed_at=timezone.now(),
        )
        open_task_secondary = EditorialTask.objects.create(
            work=work_secondary,
            recipient=self.chief,
            sender=self.author,
            subject='Secondary open task',
            status=EditorialTask.Status.NEW,
        )

        self.client.force_authenticate(self.chief)
        response = self.client.get(
            f'{self.base_path}/tasks/',
            {'selected_task': str(closed_task_primary.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        results = self._extract_results(response.json())
        returned_ids = {item['id'] for item in results}
        self.assertIn(str(open_task_primary.id), returned_ids)
        self.assertNotIn(str(open_task_secondary.id), returned_ids)
