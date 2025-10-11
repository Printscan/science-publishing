from django.conf import settings
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
        'Системный код',
        max_length=32,
        choices=Code.choices,
        unique=True,
        help_text='Фиксированное значение, используемое в логике системы.'
    )
    name = models.CharField(
        'Название',
        max_length=255,
        unique=True,
        help_text='Человекочитаемое имя роли.'
    )
    description = models.TextField(
        'Описание',
        blank=True,
        default='',
        help_text='Дополнительная информация для администраторов.'
    )

    class Meta:
        verbose_name = 'Роль издательства'
        verbose_name_plural = 'Роли издательства'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    """Расширение базового пользователя для научного издательства."""

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
        'ФИО',
        max_length=255,
        blank=True,
        default='',
        help_text='Отображается в выходных данных и публичных карточках.'
    )
    organization = models.CharField(
        'Организация',
        max_length=255,
        blank=True,
        default='',
        help_text='Основное место работы или подразделение.'
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
        max_length=32,
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
        'Биография / компетенции',
        blank=True,
        default=''
    )
    is_active = models.BooleanField(
        'Активен в издательстве',
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
        verbose_name = 'Профиль участника'
        verbose_name_plural = 'Профили участников'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self) -> str:
        return self.display_name or self.user.get_full_name() or self.user.get_username()


class UserProfileRole(models.Model):
    """Фиксация ролей пользователя с дополнительными атрибутами."""

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
        verbose_name='Назначено пользователем',
        help_text='Кто выдал доступ; пусто, если назначение автоматическое.'
    )
    assigned_at = models.DateTimeField(
        'Дата назначения',
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        'Срок действия',
        null=True,
        blank=True,
        help_text='Если указано, роль будет истекать в заданную дату.'
    )
    notes = models.TextField(
        'Комментарии',
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Роль профиля'
        verbose_name_plural = 'Роли профиля'
        unique_together = [('profile', 'role')]
        ordering = ['profile__user__last_name', 'role__name']

    def __str__(self) -> str:
        return f'{self.profile} — {self.role}'
