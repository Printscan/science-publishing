from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from modules.science_publishing.api.models import (
    EditorialRole,
    UserProfile,
    UserProfileRole,
    Work,
)


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

        # Проверяем, что чат содержит записи по ключевым шагам
        self.client.force_authenticate(self.chief)
        chat_resp = self.client.get(f'{self.base_path}/works/{work.id}/chat/')
        self.assertEqual(chat_resp.status_code, status.HTTP_200_OK, chat_resp.content)
        messages = chat_resp.json()
        self.assertGreaterEqual(len(messages), 3)
        actions = {msg.get('metadata', {}).get('action') for msg in messages}
        self.assertIn('assign_editor', actions)
        self.assertIn('editor_approve', actions)
        self.assertIn('chief_approve', actions)

    def test_chat_visibility_for_roles(self):
        work = self._create_work()
        outsider = get_user_model().objects.create_user(username='outsider', password='123')

        # Назначаем редактора, чтобы чат и статус обновились
        self.client.force_authenticate(self.chief)
        assign_url = f'{self.base_path}/works/{work.id}/assign-editor/'
        self.client.post(assign_url, {'editor_profile': str(self.editor_profile.id)}, format='json')

        # Редактор пишет сообщение
        self.client.force_authenticate(self.editor)
        post_resp = self.client.post(
            f'{self.base_path}/works/{work.id}/chat/',
            {'content': 'Привет, посмотрел черновик.'},
            format='json',
        )
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED, post_resp.content)

        # Автор видит переписку
        self.client.force_authenticate(self.author)
        chat_resp = self.client.get(f'{self.base_path}/works/{work.id}/chat/')
        self.assertEqual(chat_resp.status_code, status.HTTP_200_OK, chat_resp.content)
        self.assertTrue(
            any(msg.get('content') == 'Привет, посмотрел черновик.' for msg in chat_resp.json())
        )

        # Посторонний пользователь не имеет доступа
        self.client.force_authenticate(outsider)
        forbidden = self.client.get(f'{self.base_path}/works/{work.id}/chat/')
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
