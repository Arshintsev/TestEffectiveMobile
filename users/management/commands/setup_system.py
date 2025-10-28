import getpass

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.validators import validate_email

from users.models import AccessRule, CustomUser, Element, Role


class Command(BaseCommand):
    help = 'Создает базовые роли, администратора и правила доступа'

    def handle(self, *args, **options):
        self.stdout.write("Настройка системы...")
        self.stdout.write("Применяем миграции...")
        call_command('makemigrations', interactive=False)  # создаёт миграции (опционально)
        call_command('migrate', interactive=False)  # применяет миграции

        #  Создаем роли
        admin_role, _ = Role.objects.get_or_create(
            name=Role.ADMIN, defaults={'description': 'Администратор'}
        )
        manager_role, _ = Role.objects.get_or_create(
            name=Role.MANAGER, defaults={'description': 'Менеджер'}
        )
        user_role, _ = Role.objects.get_or_create(
            name=Role.USER, defaults={'description': 'Пользователь'}
        )

        # Создаем администратора и сохраняем ссылку на него
        admin_user = self.create_admin(admin_role)

        # Создаем элементы и проставляем владельца (admin_user)
        elements_names = ['Product', 'Store', 'Order', 'AccessRule']
        elements = []
        for name in elements_names:
            element, _ = Element.objects.get_or_create(
                name=name,
                defaults={'owner': admin_user}
            )
            elements.append(element)

        #  Настраиваем AccessRule для всех ролей
        self.create_access_rules(admin_role, manager_role, user_role, elements)

        self.stdout.write(self.style.SUCCESS("Система настроена!"))

    def create_admin(self, admin_role):
        """Создание администратора с вводом данных в консоли."""
        self.stdout.write("\nСоздание администратора:")

        email = self.get_valid_email()
        first_name = input("Имя: ").strip()
        last_name = input("Фамилия: ").strip()
        password = self.get_valid_password()

        admin_user = CustomUser(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=admin_role
        )
        admin_user.set_password(password)
        admin_user.save()

        self.stdout.write(self.style.SUCCESS(f"Администратор создан: {email}"))

        return admin_user

    def get_valid_email(self):
        """Проверка корректности и уникальности email."""
        while True:
            email = input("Email: ").strip()
            try:
                validate_email(email)
                if not CustomUser.objects.filter(email=email).exists():
                    return email
                self.stdout.write("Ошибка: Email уже существует")
            except Exception:
                self.stdout.write("Ошибка: Введите корректный email")

    def get_valid_password(self):
        """Проверка длины и подтверждение пароля."""
        while True:
            password = getpass.getpass("Пароль: ")
            if len(password) >= 8:
                password_confirm = getpass.getpass("Подтверждение пароля: ")
                if password == password_confirm:
                    return password
                self.stdout.write("Ошибка: Пароли не совпадают")
            else:
                self.stdout.write("Ошибка: Пароль должен быть не менее 8 символов")

    def create_access_rules(self, admin_role, manager_role, user_role, elements):
        """Создание правил доступа для каждой роли и типа объекта."""
        for element in elements:
            ct = ContentType.objects.get_for_model(element.__class__)

            # Админ — всё может
            AccessRule.objects.get_or_create(
                role=admin_role,
                content_type=ct,
                defaults={
                    'read_permission': True,
                    'create_permission': True,
                    'update_permission': True,
                    'delete_permission': True,
                    'read_all_permission': True,
                    'update_all_permission': True,
                    'delete_all_permission': True
                }
            )

            # Менеджер — видит все, редактирует свои
            AccessRule.objects.get_or_create(
                role=manager_role,
                content_type=ct,
                defaults={
                    'read_permission': True,
                    'create_permission': True,
                    'update_permission': True,
                    'delete_permission': True,
                    'read_all_permission': True,
                    'update_all_permission': True,
                    'delete_all_permission': False
                }
            )

            # Пользователь — видит и редактирует только свои
            AccessRule.objects.get_or_create(
                role=user_role,
                content_type=ct,
                defaults={
                    'read_permission': True,
                    'create_permission': True,
                    'update_permission': True,
                    'delete_permission': True,
                    'read_all_permission': False,
                    'update_all_permission': False,
                    'delete_all_permission': False
                }
            )
