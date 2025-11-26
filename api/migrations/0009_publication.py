import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('science_publishing', '0008_editorialtask_linked_list'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('author_full_name', models.CharField(blank=True, default='', max_length=255, verbose_name='Полное имя автора')),
                ('publication_kind', models.CharField(choices=[('method_guidelines', 'Методические рекомендации'), ('lab_practicum', 'Лабораторный практикум'), ('textbook', 'Учебник'), ('monograph', 'Монография'), ('article', 'Статья'), ('theses', 'Тезисы')], max_length=32, verbose_name='Тип публикации')),
                ('guideline_subtype', models.CharField(blank=True, choices=[('coursework', 'Курсовая работа'), ('laboratory', 'Лабораторная работа'), ('practical', 'Практическое пособие')], default='', help_text='Используется для публикаций типа "Методические рекомендации".', max_length=32, verbose_name='Подтип методических материалов')),
                ('discipline_name', models.CharField(max_length=255, verbose_name='Название дисциплины')),
                ('discipline_topic', models.CharField(blank=True, default='', max_length=255, verbose_name='Тема дисциплины')),
                ('rector_name', models.CharField(blank=True, default='', max_length=255, verbose_name='Ректор')),
                ('year', models.PositiveIntegerField(verbose_name='Год')),
                ('pages_count', models.PositiveIntegerField(default=0, verbose_name='Количество страниц')),
                ('udc', models.CharField(blank=True, default='', max_length=64, verbose_name='УДК')),
                ('bbk', models.CharField(blank=True, default='', max_length=64, verbose_name='ББК')),
                ('developers', models.CharField(blank=True, default='', max_length=255, verbose_name='Разработчики')),
                ('scientific_editor', models.CharField(blank=True, default='', max_length=255, verbose_name='Научный редактор')),
                ('computer_layout', models.CharField(blank=True, default='', max_length=255, verbose_name='Компьютерная верстка')),
                ('co_authors', models.CharField(blank=True, default='', max_length=255, verbose_name='Соавторы')),
                ('training_form', models.CharField(choices=[('full_time', 'Очная'), ('part_time', 'Заочная'), ('mixed', 'Очно-заочная')], max_length=32, verbose_name='Форма обучения')),
                ('faculty', models.CharField(blank=True, default='', max_length=255, verbose_name='Факультет')),
                ('department', models.CharField(blank=True, default='', max_length=255, verbose_name='Кафедра')),
                ('short_description', models.TextField(blank=True, default='', verbose_name='Краткое описание')),
                ('document', models.FileField(blank=True, null=True, upload_to='science_publishing/works/%Y/%m/', verbose_name='Файл публикации')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('pending_chief_review', 'Ожидает главного редактора'), ('in_editor_review', 'В работе у редактора'), ('waiting_for_author', 'Ожидает правок автора'), ('ready_for_chief_approval', 'Ожидает утверждения главреда'), ('published', 'Опубликована')], db_index=True, default='published', max_length=64, verbose_name='Статус')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлена')),
                ('current_editor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edited_publications', to='science_publishing.userprofile', verbose_name='Ответственный редактор')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publications', to='science_publishing.userprofile', verbose_name='Профиль автора')),
                ('source_work', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='publication', to='science_publishing.work', verbose_name='Исходная работа')),
            ],
            options={
                'verbose_name': 'Публикация',
                'verbose_name_plural': 'Публикации',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='publication',
            index=models.Index(fields=['profile', 'year'], name='science_pub_profile_ye_cf2703_idx'),
        ),
        migrations.AddIndex(
            model_name='publication',
            index=models.Index(fields=['publication_kind'], name='science_pub_publica_4e3e67_idx'),
        ),
        migrations.AddIndex(
            model_name='publication',
            index=models.Index(fields=['status'], name='science_pub_status_4ba85d_idx'),
        ),
    ]

