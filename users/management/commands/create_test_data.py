from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


SKILLS = [
    'Python', 'Django', 'JavaScript', 'React',
    'PostgreSQL', 'Docker', 'CSS', 'HTML', 'Git', 'FastAPI',
]

USERS = [
    {
        'email': 'maria@yandex.ru',
        'name': 'Мария',
        'surname': 'Крутая',
        'password': 'password',
        'about': 'Frontend-разработчик с 30-летним опытом. Люблю создавать красивые интерфейсы.',
        'phone': '+79131865678',
        'github_url': '',
        'skills': ['JavaScript', 'React', 'CSS', 'HTML'],
    },
    {
        'email': 'alex@gmail.com',
        'name': 'Александр',
        'surname': 'Заливайкин',
        'password': 'password',
        'about': 'Backend-разработчик на Python и Django. Интересуюсь архитектурой микросервисов.',
        'phone': '+79262345678',
        'github_url': '',
        'skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
    },
    {
        'email': 'elena@mail.ru',
        'name': 'Елена',
        'surname': 'Красавица',
        'password': 'password',
        'about': 'Full-stack разработчик. Работаю с React и FastAPI. Ищу интересные проекты.',
        'phone': '',
        'github_url': '',
        'skills': ['Python', 'FastAPI', 'React', 'JavaScript', 'Git'],
    },
    {
        'email': 'dmitry@yandex.ru',
        'name': 'Дмитрий',
        'surname': 'Незабывваемый',
        'password': 'password',
        'about': 'DevOps-инженер. Настраиваю CI/CD, работаю с Docker и Kubernetes.',
        'phone': '+79283981234',
        'github_url': '',
        'skills': ['Docker', 'Git', 'Python'],
    },
]

PROJECTS = [
    {
        'owner_email': 'maria@yandex.ru',
        'name': 'TaskBoard — канбан для команд',
        'description': (
            'Веб-приложение для управления задачами в стиле канбан. '
            'Ищу бэкенд-разработчика на Django и дизайнера.'
        ),
        'github_url': '',
        'status': 'open',
    },
    {
        'owner_email': 'alex@gmail.com',
        'name': 'OpenBudget — трекер личных финансов',
        'description': (
            'Приложение для учёта личных финансов с аналитикой и визуализацией расходов. '
            'Стек: Django REST Framework + React. Ищу frontend-разработчика.'
        ),
        'github_url': '',
        'status': 'open',
    },
    {
        'owner_email': 'alex@gmail.com',
        'name': 'DevNews — агрегатор IT-новостей',
        'description': (
            'Агрегатор новостей для разработчиков: парсинг RSS-лент, персонализация ленты, '
            'возможность сохранять статьи и делиться ими. Уже в работе, нужен помощник.'
        ),
        'github_url': '',
        'status': 'closed',
    },
    {
        'owner_email': 'elena@mail.ru',
        'name': 'PetMatch — платформа для усыновления животных',
        'description': (
            'Сайт для поиска питомцев из приютов. Фильтрация по породе, возрасту и городу, '
            'личный кабинет для приютов и заявка на усыновление. '
            'Стек: FastAPI + React. Нужен дизайнер и тестировщик.'
        ),
        'github_url': '',
        'status': 'open',
    },
    {
        'owner_email': 'dmitry@yandex.ru',
        'name': 'AutoDeploy — CI/CD конструктор',
        'description': (
            'Визуальный конструктор пайплайнов для CI/CD без написания YAML вручную. '
            'Генерирует конфигурации для GitHub Actions и GitLab CI. '
            'Ищу фронтенд-разработчика с опытом работы с графическими редакторами.'
        ),
        'github_url': '',
        'status': 'open',
    },
]


class Command(BaseCommand):
    help = 'Создать тестовые данные: пользователей, навыки и проекты'

    def handle(self, *args, **options):
        self.stdout.write('Создание навыков...')
        skills_map = {}
        for name in SKILLS:
            skill, created = Skill.objects.get_or_create(name=name)
            skills_map[name] = skill
            if created:
                self.stdout.write(f'  + Навык: {name}')

        self.stdout.write('Создание пользователей...')
        users_map = {}
        for data in USERS:
            skill_names = data.pop('skills')
            password = data.pop('password')
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={k: v for k, v in data.items() if k != 'email'},
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    f'  + Пользователь: {user.name} {user.surname} ({user.email})'
                )
            else:
                self.stdout.write(f'  ~ Уже существует: {user.email}')
            for skill_name in skill_names:
                user.skills.add(skills_map[skill_name])
            users_map[data['email']] = user

        self.stdout.write('Создание проектов...')
        for data in PROJECTS:
            owner_email = data.pop('owner_email')
            owner = users_map[owner_email]
            project, created = Project.objects.get_or_create(
                name=data['name'],
                owner=owner,
                defaults={k: v for k, v in data.items() if k != 'name'},
            )
            if created:
                self.stdout.write(
                    f'  + Проект: «{project.name}» (автор: {owner.name} {owner.surname})'
                )
            else:
                self.stdout.write(f'  ~ Уже существует: «{project.name}»')

        self.stdout.write(self.style.SUCCESS('\nГотово! Тестовые данные созданы.'))
        self.stdout.write('Тестовый аккаунт: maria@yandex.ru / password')
