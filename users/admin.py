#
#
#
# from django.contrib import admin
#
# from .models import CustomUser, Element
#
# # Register your models here.
#
# @admin.register(Element)
# class ElementAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'description', 'owner')
#     search_fields = ('name',)
#
#
# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'first_name', 'last_name', 'middle_name',
#                     'email', 'is_active', 'role', 'created_at')
#     search_fields = ('first_name', 'last_name', 'email')
#     list_editable = ('is_active',)
#     list_filter = ('created_at', 'is_active', 'role')
#
#     # Убираем поле password_hash из формы редактирования
#     exclude = ('password_hash',)
#
#     # Запрещаем создание пользователей через админку
#     def has_add_permission(self, request):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         """Запрещаем удаление через админку"""
#         return False
#
