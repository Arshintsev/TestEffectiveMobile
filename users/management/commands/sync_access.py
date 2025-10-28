from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from users.models import AccessRule, Role


class Command(BaseCommand):
    help = ("Синхронизирует права доступа (AccessRule) для всех моделей,"
            "создавая недостающие записи")

    def handle(self, *args, **options):
        self.stdout.write("Синхронизация AccessRule для всех моделей...")

        # Загружаем все роли
        roles = {
            Role.ADMIN: Role.objects.get_or_create(
                name=Role.ADMIN,
                defaults={'description': 'Администратор'}
            )[0],
            Role.MANAGER: Role.objects.get_or_create(
                name=Role.MANAGER,
                defaults={'description': 'Менеджер'}
            )[0],
            Role.USER: Role.objects.get_or_create(
                name=Role.USER,
                defaults={'description': 'Пользователь'}
            )[0],
        }


        # Шаблон прав по умолчанию
        default_permissions = {
            Role.ADMIN: {
                'read_permission': True,
                'create_permission': True,
                'update_permission': True,
                'delete_permission': True,
                'read_all_permission': True,
                'update_all_permission': True,
                'delete_all_permission': True,
            },
            Role.MANAGER: {
                'read_permission': True,
                'create_permission': True,
                'update_permission': True,
                'delete_permission': True,
                'read_all_permission': True,
                'update_all_permission': True,
                'delete_all_permission': False,
            },
            Role.USER: {
                'read_permission': True,
                'create_permission': True,
                'update_permission': True,
                'delete_permission': True,
                'read_all_permission': False,
                'update_all_permission': False,
                'delete_all_permission': False,
            },
        }

        # Перебираем все модели
        created_count = 0
        for ct in ContentType.objects.all():
            model = ct.model_class()
            if not model or model._meta.app_label in ["contenttypes", "admin", "auth",
                                                      "sessions", "token_blacklist",
                                                      "users"]:
                continue

            for role_key, role in roles.items():
                exists = AccessRule.objects.filter(role=role,
                                                   content_type=ct).exists()
                if not exists:
                    AccessRule.objects.create(role=role,
                                              content_type=ct,
                                              **default_permissions[role_key])
                    self.stdout.write(
                        f"Создан AccessRule: {role.name} → {ct.app_label}.{ct.model}"
                    )
                    created_count += 1

        if created_count == 0:
            self.stdout.write(self.style.WARNING("Новых моделей не найдено."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Синхронизация завершена: добавлено {created_count} записей.")
            )
