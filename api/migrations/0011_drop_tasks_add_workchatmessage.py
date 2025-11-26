import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('science_publishing', '0010_migrate_published_to_publications'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EditorialTaskMessage',
        ),
        migrations.DeleteModel(
            name='EditorialTask',
        ),
        migrations.CreateModel(
            name='WorkChatMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('content', models.TextField(blank=True, default='', verbose_name='Сообщение')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Структурированные сведения об изменениях, вложениях и прочем контексте.', verbose_name='Дополнительные данные')),
                ('is_system', models.BooleanField(default=False, help_text='Помечает автоматические записи, созданные системой.', verbose_name='Системное сообщение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('author', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='science_publishing_chat_messages', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('work', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='chat_messages', to='science_publishing.work', verbose_name='Работа')),
            ],
            options={
                'verbose_name': 'Сообщение чата работы',
                'verbose_name_plural': 'Сообщения чатов работ',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='workchatmessage',
            index=models.Index(fields=['work', 'created_at'], name='science_pub_work_chat_idx'),
        ),
    ]
