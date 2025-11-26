from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from ...models import EditorialRole, UserProfile, UserProfileRole


DEFAULT_USERS = [
    {
        "username": "editor1",
        "password": "editor123",
        "email": "editor1@example.com",
        "first_name": "Елена",
        "last_name": "Редактор",
        "role": EditorialRole.Code.EDITOR,
    },
    {
        "username": "chief1",
        "password": "chief123",
        "email": "chief1@example.com",
        "first_name": "Галина",
        "last_name": "Главред",
        "role": EditorialRole.Code.CHIEF_EDITOR,
    },
    {
        "username": "reviewer1",
        "password": "reviewer123",
        "email": "reviewer1@example.com",
        "first_name": "Роман",
        "last_name": "Рецензент",
        "role": EditorialRole.Code.REVIEWER,
    },
]


class Command(BaseCommand):
    help = (
        "Создаёт трёх пользователей для контура научных публикаций: редактор, главный редактор, рецензент.\n"
        "Если пользователи уже есть — роли и профиль будут обеспечены, а пароль не меняется без флага --reset-password."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Принудительно сбросить пароли существующих пользователей на значения по умолчанию",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset_password = options.get("reset_password", False)
        User = get_user_model()

        # Ensure roles exist (idempotent)
        roles_to_ensure = [
            (EditorialRole.Code.EDITOR, "Редактор", "Редактирует тексты и загружает правки."),
            (EditorialRole.Code.CHIEF_EDITOR, "Главный редактор", "Утверждает выпуск и распределяет задачи."),
            (EditorialRole.Code.REVIEWER, "Рецензент", "Проводит экспертную проверку материалов."),
        ]
        for code, name, desc in roles_to_ensure:
            EditorialRole.objects.update_or_create(
                code=code, defaults={"name": name, "description": desc}
            )

        created_any = False
        for spec in DEFAULT_USERS:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                },
            )

            if created:
                user.set_password(spec["password"])
                user.save(update_fields=["password"])  # ensure password hash saved
            elif reset_password:
                user.set_password(spec["password"])
                user.save(update_fields=["password"])  # reset password when requested

            # Ensure profile exists
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={"display_name": f"{spec['first_name']} {spec['last_name']}".strip()},
            )

            # Ensure role assignment exists
            role = EditorialRole.objects.get(code=spec["role"])  # guaranteed above
            UserProfileRole.objects.get_or_create(profile=profile, role=role)

            status = "создан" if created else "обновлён"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Пользователь {user.username} ({spec['first_name']} {spec['last_name']}) {status}. Роль: {role.name}."
                )
            )
            if created or reset_password:
                self.stdout.write(f"  Пароль: {spec['password']}")
                created_any = True

        if not created_any:
            self.stdout.write("Готово. Данные пользователей актуальны; пароли не менялись.")

