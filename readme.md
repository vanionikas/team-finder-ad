# TeamFinder — платформа для поиска команды

Веб-приложение, на котором разработчики и другие специалисты могут находить единомышленников для совместной работы над pet-проектами.

**Реализован вариант №2**: навыки пользователей и фильтрация участников по навыкам.

---


### Требования

- Python 3.12+
- Docker и Docker Compose

---

### 1. Клонировать репозиторий

```bash
git clone <url-репозитория>
cd team-finder-ad
```

---

### 2. Создать виртуальное окружение и установить зависимости

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 3. Создать файл `.env`

Скопировать пример:
```bash
cp .env_example .env
```

Содержимое `.env` (готово к использованию с Docker Compose):
```env
DJANGO_SECRET_KEY=django-insecure-teamfinder-dev-secret-key-change-in-production
DJANGO_DEBUG=True

POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

TASK_VERSION=2
```

> `TASK_VERSION=2` определяет, что используются шаблоны из `templates_var2`.

---

### 4. Запустить базу данных

```bash
docker compose up -d
```

База данных PostgreSQL будет доступна на `localhost:5432`.

---

### 5. Применить миграции

```bash
python manage.py migrate
```

---

### 6. Создать тестовые данные

```bash
python manage.py create_test_data
```

Будут созданы следующие тестовые аккаунты (пароль у всех: `password`):

| Email                | Имя                    | Навыки                              |
|----------------------|------------------------|-------------------------------------|
| maria@yandex.ru      | Мария Крутая           | JavaScript, React, CSS, HTML        |
| alex@gmail.com       | Александр Заливайкин   | Python, Django, PostgreSQL, Docker  |
| elena@mail.ru        | Елена Красавица        | Python, FastAPI, React, JavaScript  |
| dmitry@yandex.ru     | Дмитрий Незабывваемый  | Docker, Git, Python                 |

Каждый пользователь имеет один или несколько проектов.

---

### 7. Создать суперпользователя (опционально)

```bash
python manage.py createsuperuser
```

Панель администратора доступна по адресу `/admin/`.

---

### 8. Запустить сервер разработки

```bash
python manage.py runserver
```

Приложение доступно по адресу: **http://localhost:8000**

---

### 9. Запустить автотесты

Тесты используют SQLite и не требуют запущенного PostgreSQL:

```bash
python manage.py test --settings=team_finder.settings_test
```

Ожидаемый результат: `Ran 49 tests in ...s OK`

---

## Реализованный функционал

### Общая функциональность (все страницы и функции)

- **Главная страница** `/projects/list` — список проектов с пагинацией (12 на страницу), сортировка по дате (новые сверху)
- **Регистрация** `/users/register/` — форма с полями: имя, фамилия, email, пароль; после — редирект на вход
- **Вход** `/users/login/` — аутентификация по email и паролю
- **Выход** `/users/logout/`
- **Профиль пользователя** `/users/<id>/` — аватар, ФИО, описание, контакты, проекты
- **Редактирование профиля** `/users/edit-profile/` — обновление личных данных, аватара
- **Смена пароля** `/users/change-password/`
- **Страница проекта** `/projects/<id>` — детали проекта, участники, кнопки владельца
- **Создание проекта** `/projects/create-project`
- **Редактирование проекта** `/projects/<id>/edit`
- **Завершение проекта** — AJAX, меняет статус на «Закрыт»
- **Участие в проекте** — AJAX-toggle «Участвовать / Отказаться»
- **Список пользователей** `/users/list` — карточки с пагинацией (12 на страницу)

### Вариант №2: Навыки пользователей

- **Блок навыков** на странице профиля
- **Добавление навыков** — AJAX-автодополнение, создание нового навыка если его нет в базе
- **Удаление навыков** — AJAX, без перезагрузки страницы
- **Фильтр по навыкам** на странице `/users/list` — `?skill=<Название>`
- Активный фильтр подсвечивается, есть кнопка «Сбросить»

---

## Структура проекта

```
team-finder-ad/
├── users/               # Приложение: пользователи, навыки, аутентификация
│   ├── management/commands/create_test_data.py
│   ├── models.py        # User, Skill
│   ├── views.py         # Все views для пользователей
│   ├── forms.py
│   ├── urls.py
│   └── tests.py
├── projects/            # Приложение: проекты
│   ├── models.py        # Project
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── tests.py
├── team_finder/         # Настройки Django
├── templates_var2/      # HTML-шаблоны (вариант №2)
├── static/              # CSS, JS, изображения
├── docker-compose.yml
├── requirements.txt
└── .env_example
```
