## Система аутентификации и авторизации (DRF + JWT + SQlite)
Проект реализует собственную систему аутентификации и авторизации без использования стандартного Django User/AbstractUser.

### Обзор
Проект реализует:
- Регистрацию, логин по email+пароль, логаут (с добавлением в blacklist refresh token), редактирование профиля, смену пароля, soft-delete пользователя.
- Ролевую модель и правила доступа к объектам через таблицу `access_rules`.
- Mock-объект `Element` и CRUD API с проверкой прав.
- Идентификация через JWT в заголовке `Authorization: Bearer <access>`.

Технологии: Django 5, DRF, SimpleJWT, bcrypt, ContentTypes, SQLite (можно заменить Postgres).

### Модели
- `users.CustomUser`: `email` (уникальный), ФИО, `password_hash` (bcrypt), `is_active`, `deleted_at`, `role -> Role`.
- `users.Role`: константы `ADMIN`, `MANAGER`, `USER`.
- `users.AccessRule`: `(role, content_type)` + флаги прав: `read|create|update|delete` и `read_all|update_all|delete_all`.
- `users.Element`: `name`, `description`, `owner -> CustomUser`.

### Аутентификация и авторизация
- Аутентификация: SimpleJWT (access/refresh).
- Авторизация: `elements.permissions.RoleAccessPermission` использует `AccessRule` и владельца объекта.

### Логика проверки прав
1. Определяем пользователя через JWT (`Authorization: Bearer <access>`).  
2. Проверяем активность пользователя (`is_active=True`).  
3. Получаем правило из `AccessRule` по роли и типу модели.  
4. Если ресурс принадлежит пользователю → применяем `*_permission`.  
   Если ресурс чужой → применяем `*_all_permission`.  
5. В случае нарушения прав:
   - 401 Unauthorized — пользователь не найден или заблокирован.
   - 403 Forbidden — действие запрещено.

### Эндпоинты
Все пути ниже подключены в корневом `urls.py` 

#### Auth (`my_auth.urls`)
- POST `api/register` — регистрация (возвращает `access`, `refresh`).
- POST `api/login/` — логин (получение `access`, `refresh`).
- POST `api/logout` — логаут (нужно передать `refresh` для blacklist).
- GET/PUT `api/update` — получить/обновить свой профиль.
- PUT `api/profile/change-password` — смена пароля (старый/новый/подтверждение).
- DELETE `api/profile/delete` — soft-delete (блокирует пользователя и токены).
- GET/PUT/DELETE `api/users/<id>` — операции над пользователями (только админ).
- GET `api/users` — список активных пользователей (авторизованные).
- POST `api/token/refresh/`, POST `api/token/verify/` — SimpleJWT.

#### Elements (`elements.urls`)
- CRUD `api/elements/` — доступ по `RoleAccessPermission`:
  - GET: если `read_all_permission` или `read_permission` только свои.
  - POST: если `create_permission` (owner ставится автоматически текущим пользователем).
  - PUT/PATCH: если `update_all_permission` или `update_permission` для своих.
  - DELETE: если `delete_all_permission` или `delete_permission` для своих.
Примечание: Element — пример бизнес-объекта для демонстрации авторизации.

#### Access rules (`users.urls`) — CRUD для администратора
Требует заголовок `Authorization: Bearer <access>` и роль `admin`.

- GET `api/access-rules/` — список правил.
- POST `api/access-rules/` — создать правило.
- GET `api/access-rules/<id>/` — получить правило.
- PUT/PATCH `api/access-rules/<id>/` — обновить правило.
- DELETE `api/access-rules/<id>/` — удалить правило.
- get `api/access-rules/by-model/product/` -получить правило конкретной медели

Поля объекта `AccessRule`:
```json
{
  "id": 1,
  "role": "admin",                
  "content_type": "product",              
  "read_permission": true,
  "create_permission": true,
  "update_permission": true,
  "delete_permission": true,
  "read_all_permission": true,
  "update_all_permission": true,
  "delete_all_permission": true
}
```

Валидация: правило уникально в паре `(role, content_type)`.

### Инициализация
- Установите зависимости из requirements.txt (pip install -r requirements.txt)
- Переименуйте .env.example в .env
- Добавьте в .env ваш секретный ключ
- 
- `python manage.py setup_system` — создает стартовые миграции, роли, администратора, тестовые `Element`, базовые правила.
- `python manage.py sync_access` — добавляет недостающие `AccessRule` для всех моделей (кроме системных) при добавлении новых моделей.
Примечание: стандартная команда createsuperuser не работает, так как используется кастомная модель CustomUser без наследования от AbstractUser. Для создания администратора используется кастомная команда setup_system
- 
### Настройки окружения
Через `python-decouple`:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_ENGINE`, `DB_NAME`.


