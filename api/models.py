import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EditorialRole(models.Model):
    """Справочник ролей участников издательского контура."""

    class Code(models.TextChoices):
        AUTHOR = 'author', 'Автор'
        CHIEF_EDITOR = 'chief_editor', 'Главный редактор'
        EDITOR = 'editor', 'Редактор'
        ADMINISTRATOR = 'administrator', 'Администратор'
        REVIEWER = 'reviewer', 'Рецензент'

    code = models.CharField(
        'Код роли',
        max_length=32,
        choices=Code.choices,
        unique=True,
        help_text='Уникальный символьный код роли, используется в проверках прав.'
    )
    name = models.CharField(
        'Название',
        max_length=255,
        unique=True,
        help_text='Отображаемое наименование роли.'
    )
    description = models.TextField(
        'Описание',
        blank=True,
        default='',
        help_text='Дополнительная информация о назначении роли.'
    )

    class Meta:
        verbose_name = 'Роль редакционного контура'
        verbose_name_plural = 'Роли редакционного контура'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class PublicationKind(models.TextChoices):
    METHOD_GUIDELINES = 'method_guidelines', 'Методические рекомендации'
    LAB_PRACTICUM = 'lab_practicum', 'Лабораторный практикум'
    TEXTBOOK = 'textbook', 'Учебник'
    MONOGRAPH = 'monograph', 'Монография'
    ARTICLE = 'article', 'Статья'
    THESES = 'theses', 'Тезисы'


class GuidelineSubtype(models.TextChoices):
    COURSE = 'coursework', 'Курсовая работа'
    LAB = 'laboratory', 'Лабораторная работа'
    PRACTICAL = 'practical', 'Практическое пособие'


class TrainingForm(models.TextChoices):
    FULL_TIME = 'full_time', 'Очная'
    PART_TIME = 'part_time', 'Заочная'
    MIXED = 'mixed', 'Очно-заочная'


class UserProfile(models.Model):
    """Профиль пользователя модуля научных публикаций."""

    id = models.UUIDField(
        'Идентификатор',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='science_publishing_profile',
        verbose_name='Пользователь'
    )
    roles = models.ManyToManyField(
        EditorialRole,
        related_name='profiles',
        through='UserProfileRole',
        blank=True,
        verbose_name='Роли'
    )
    display_name = models.CharField(
        'Отображаемое имя',
        max_length=255,
        blank=True,
        default='',
        help_text='Имя, которое показывается в интерфейсе. Если не заполнено используется ФИО или логин.'
    )
    organization = models.CharField(
        'Организация',
        max_length=255,
        blank=True,
        default=''
    )
    department = models.CharField(
        'Подразделение',
        max_length=255,
        blank=True,
        default=''
    )
    position = models.CharField(
        'Должность',
        max_length=255,
        blank=True,
        default=''
    )
    academic_degree = models.CharField(
        'Учёная степень',
        max_length=255,
        blank=True,
        default=''
    )
    academic_title = models.CharField(
        'Учёное звание',
        max_length=255,
        blank=True,
        default=''
    )
    phone = models.CharField(
        'Телефон',
        max_length=64,
        blank=True,
        default=''
    )
    orcid = models.CharField(
        'ORCID',
        max_length=32,
        blank=True,
        default=''
    )
    scopus_id = models.CharField(
        'Scopus Author ID',
        max_length=32,
        blank=True,
        default=''
    )
    elibrary_id = models.CharField(
        'eLIBRARY ID',
        max_length=32,
        blank=True,
        default=''
    )
    website = models.URLField(
        'Персональный сайт',
        blank=True,
        default=''
    )
    biography = models.TextField(
        'Биография',
        blank=True,
        default=''
    )
    is_active = models.BooleanField(
        'Активен',
        default=True
    )
    created_at = models.DateTimeField(
        'Создан',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлён',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self) -> str:
        return self.display_name or self.user.get_full_name() or self.user.get_username()


class Work(models.Model):
    """Научная работа пользователя со всеми редакционными атрибутами."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PENDING_CHIEF_REVIEW = 'pending_chief_review', 'Ожидает главного редактора'
        IN_EDITOR_REVIEW = 'in_editor_review', 'В работе у редактора'
        WAITING_FOR_AUTHOR = 'waiting_for_author', 'Ожидает правок автора'
        READY_FOR_CHIEF_APPROVAL = 'ready_for_chief_approval', 'Ожидает утверждения главреда'
        PUBLISHED = 'published', 'Опубликована'

    id = models.UUIDField(
        'Идентификатор',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Профиль автора'
    )
    author_full_name = models.CharField(
        'Полное имя автора',
        max_length=255,
        blank=True,
        default=''
    )
    publication_kind = models.CharField(
        'Тип публикации',
        max_length=32,
        choices=PublicationKind.choices
    )
    guideline_subtype = models.CharField(
        'Подтип методических материалов',
        max_length=32,
        choices=GuidelineSubtype.choices,
        blank=True,
        default='',
        help_text='Используется для публикаций типа "Методические рекомендации".'
    )
    discipline_name = models.CharField(
        'Название дисциплины',
        max_length=255
    )
    discipline_topic = models.CharField(
        'Тема дисциплины',
        max_length=255,
        blank=True,
        default=''
    )
    rector_name = models.CharField(
        'Ректор',
        max_length=255,
        blank=True,
        default=''
    )
    year = models.PositiveIntegerField('Год')
    pages_count = models.PositiveIntegerField(
        'Количество страниц',
        default=0
    )
    udc = models.CharField(
        'УДК',
        max_length=64,
        blank=True,
        default=''
    )
    bbk = models.CharField(
        'ББК',
        max_length=64,
        blank=True,
        default=''
    )
    developers = models.CharField(
        'Разработчики',
        max_length=255,
        blank=True,
        default=''
    )
    scientific_editor = models.CharField(
        'Научный редактор',
        max_length=255,
        blank=True,
        default=''
    )
    computer_layout = models.CharField(
        'Компьютерная верстка',
        max_length=255,
        blank=True,
        default=''
    )
    co_authors = models.CharField(
        'Соавторы',
        max_length=255,
        blank=True,
        default=''
    )
    training_form = models.CharField(
        'Форма обучения',
        max_length=32,
        choices=TrainingForm.choices
    )
    faculty = models.CharField(
        'Факультет',
        max_length=255,
        blank=True,
        default=''
    )
    department = models.CharField(
        'Кафедра',
        max_length=255,
        blank=True,
        default=''
    )
    short_description = models.TextField(
        'Краткое описание',
        blank=True,
        default=''
    )
    document = models.FileField(
        'Файл публикации',
        upload_to='science_publishing/works/%Y/%m/',
        blank=True,
        null=True
    )
    status = models.CharField(
        'Статус',
        max_length=64,
        choices=Status.choices,
        default=Status.PENDING_CHIEF_REVIEW,
        db_index=True
    )
    current_editor = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_works',
        verbose_name='Ответственный редактор'
    )
    published_at = models.DateTimeField(
        'Дата публикации',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        'Создана',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлена',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'
        ordering = ['-year', 'discipline_name']
        indexes = [
            models.Index(fields=['profile', 'year']),
            models.Index(fields=['publication_kind']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f'{self.discipline_name} ({self.year})'

    def clean(self) -> None:
        super().clean()
        if self.guideline_subtype and self.publication_kind != PublicationKind.METHOD_GUIDELINES:
            raise ValidationError({
                'guideline_subtype': 'Выберите подтип только для публикаций типа «Методические рекомендации».',
            })


class Publication(models.Model):
    """Отдельная таблица опубликованных работ (снимок полей работы)."""

    id = models.UUIDField(
        'Идентификатор',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    source_work = models.OneToOneField(
        Work,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publication',
        verbose_name='Исходная работа'
    )
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='publications',
        verbose_name='Профиль автора'
    )
    author_full_name = models.CharField(
        'Полное имя автора',
        max_length=255,
        blank=True,
        default=''
    )
    publication_kind = models.CharField(
        'Тип публикации',
        max_length=32,
        choices=PublicationKind.choices
    )
    guideline_subtype = models.CharField(
        'Подтип методических материалов',
        max_length=32,
        choices=GuidelineSubtype.choices,
        blank=True,
        default='',
        help_text='Используется для публикаций типа "Методические рекомендации".'
    )
    discipline_name = models.CharField(
        'Название дисциплины',
        max_length=255
    )
    discipline_topic = models.CharField(
        'Тема дисциплины',
        max_length=255,
        blank=True,
        default=''
    )
    rector_name = models.CharField(
        'Ректор',
        max_length=255,
        blank=True,
        default=''
    )
    year = models.PositiveIntegerField('Год')
    pages_count = models.PositiveIntegerField(
        'Количество страниц',
        default=0
    )
    udc = models.CharField(
        'УДК',
        max_length=64,
        blank=True,
        default=''
    )
    bbk = models.CharField(
        'ББК',
        max_length=64,
        blank=True,
        default=''
    )
    developers = models.CharField(
        'Разработчики',
        max_length=255,
        blank=True,
        default=''
    )
    scientific_editor = models.CharField(
        'Научный редактор',
        max_length=255,
        blank=True,
        default=''
    )
    computer_layout = models.CharField(
        'Компьютерная верстка',
        max_length=255,
        blank=True,
        default=''
    )
    co_authors = models.CharField(
        'Соавторы',
        max_length=255,
        blank=True,
        default=''
    )
    training_form = models.CharField(
        'Форма обучения',
        max_length=32,
        choices=TrainingForm.choices
    )
    faculty = models.CharField(
        'Факультет',
        max_length=255,
        blank=True,
        default=''
    )
    department = models.CharField(
        'Кафедра',
        max_length=255,
        blank=True,
        default=''
    )
    short_description = models.TextField(
        'Краткое описание',
        blank=True,
        default=''
    )
    document = models.FileField(
        'Файл публикации',
        upload_to='science_publishing/works/%Y/%m/',
        blank=True,
        null=True
    )
    status = models.CharField(
        'Статус',
        max_length=64,
        choices=Work.Status.choices,
        default=Work.Status.PUBLISHED,
        db_index=True
    )
    current_editor = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_publications',
        verbose_name='Ответственный редактор'
    )
    published_at = models.DateTimeField(
        'Дата публикации',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        'Создана',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлена',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['profile', 'year']),
            models.Index(fields=['publication_kind']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f'{self.discipline_name} ({self.year})'

class UserProfileRole(models.Model):
    """Назначение роли пользователю."""

    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='profile_roles',
        verbose_name='Профиль'
    )
    role = models.ForeignKey(
        EditorialRole,
        on_delete=models.CASCADE,
        related_name='role_profiles',
        verbose_name='Роль'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='science_publishing_assigned_roles',
        verbose_name='Назначил'
    )
    assigned_at = models.DateTimeField(
        'Дата назначения',
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        'Срок действия',
        null=True,
        blank=True
    )
    notes = models.TextField(
        'Комментарии',
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Назначение роли'
        verbose_name_plural = 'Назначения ролей'
        unique_together = [('profile', 'role')]
        ordering = ['profile__user__last_name', 'role__name']

    def __str__(self) -> str:
        return f'{self.profile} → {self.role}'


class WorkChatMessage(models.Model):
    """Сообщение в общем чате по работе."""

    id = models.UUIDField(
        'Идентификатор',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='Работа'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='science_publishing_chat_messages',
        verbose_name='Автор'
    )
    content = models.TextField(
        'Сообщение',
        blank=True,
        default=''
    )
    metadata = models.JSONField(
        'Дополнительные данные',
        blank=True,
        default=dict,
        help_text='Структурированные сведения об изменениях, вложениях и прочем контексте.'
    )
    is_system = models.BooleanField(
        'Системное сообщение',
        default=False,
        help_text='Помечает автоматические записи, созданные системой.'
    )
    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Сообщение чата работы'
        verbose_name_plural = 'Сообщения чатов работ'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['work', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.author} → {self.work}'
