import datetime

import bcrypt
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import PROTECT
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


def validate_password(value):
    if len(value) < 8:
        raise ValidationError("Пароль должен быть не менее 8 символов")


class CustomUser(models.Model):
    """
    Кастомная модель пользователя с дополнительными полями.
    """
    first_name = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(2, "Имя должно содержать минимум 2 символа"),
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$',  # Добавил пробелы и дефисы
                message="Имя может содержать только буквы, пробелы и дефисы"
            )
        ]
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-ЯёЁ\s\-]*$',  # * вместо + для пустых значений
                message="Фамилия может содержать только буквы, пробелы и дефисы"
            )
        ]
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Zа-яА-ЯёЁ\s\-]*$',
                message="Отчество может содержать только буквы, пробелы и дефисы"
            )
        ]
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Обязательное поле. Уникальный email пользователя.",
    )
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата регистрации")
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Последний вход"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата удаления"
    )
    role = models.ForeignKey('Role', on_delete=PROTECT)

    # Для совместимости, но не используем стандартную аутентификацию
    is_anonymous = False
    is_authenticated = True
    is_staff = False  #
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        """Читабельное представление пользователя."""
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def set_password(self, password: str):
        """Хешируем и сохраняем пароль."""
        validate_password(password)
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


    def check_password(self, password: str) -> bool:
        """Проверяем введённый пароль."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def soft_delete(self):
        """Мягкое удаление пользователя и блокировка всех токенов"""
        self.is_active = False
        self.deleted_at = datetime.datetime.now()
        self.save()

        # Черный список всех токенов пользователя
        tokens = OutstandingToken.objects.filter(user=self)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

    def restore(self):
        """Восстановление"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class Role(models.Model):
    """
    Роли пользователей
    """
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'

    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (MANAGER, 'Менеджер'),
        (USER, 'Пользователь'),
    ]

    name = models.CharField(max_length=50,
                            unique=True,
                            choices=ROLE_CHOICES
                            )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()

class Element(models.Model):
    """
    Модель объектов системы (для Mock-View)
    """
    name = models.CharField(max_length=100,
                            blank=False, null=True,
                            verbose_name="Название элемента")
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="Описание")
    owner = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='element'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Элемент"
        verbose_name_plural = "Элементы"


class AccessRule(models.Model):
    """
    Правила доступа ролей к объектам разных типов.
    Определяет, что может делать роль с каждым типом бизнес-объекта.
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    # Связь с типом объекта (Product, Order, Element и т.д.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)


    # Права на свои объекты
    read_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)

    # Права на все объекты
    read_all_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'content_type')
        verbose_name = "Правило доступа"
        verbose_name_plural = "Правила доступа"

    def __str__(self):
        return f"{self.role.name} → {self.content_type.model}"
