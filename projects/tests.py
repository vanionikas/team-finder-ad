from django.test import TestCase

from projects.models import Project
from users.models import User


def make_user(email='test@test.com', name='Иван', surname='Иванов', password='testpass123'):
    return User.objects.create_user(email=email, name=name, surname=surname, password=password)


def make_project(owner, name='Тестовый проект', description='Описание', status='open'):
    return Project.objects.create(name=name, description=description, status=status, owner=owner)


class ProjectListTest(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_list_accessible_for_guest(self):
        response = self.client.get('/projects/list')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)

    def test_list_shows_pagination(self):
        for i in range(13):
            make_project(self.owner, name=f'Проект {i}')
        response = self.client.get('/projects/list')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'page-btn')

    def test_root_redirects_to_list(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/projects/list')

    def test_create_button_only_for_authenticated(self):
        response = self.client.get('/projects/list')
        self.assertNotContains(response, '/projects/create-project')
        self.client.force_login(self.owner)
        response = self.client.get('/projects/list')
        self.assertContains(response, '/projects/create-project')


class ProjectDetailTest(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_detail_accessible_for_guest(self):
        response = self.client.get(f'/projects/{self.project.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)

    def test_detail_404_for_nonexistent(self):
        response = self.client.get('/projects/99999')
        self.assertEqual(response.status_code, 404)

    def test_detail_shows_owner_actions(self):
        self.client.force_login(self.owner)
        response = self.client.get(f'/projects/{self.project.id}')
        self.assertContains(response, 'Редактировать')
        self.assertContains(response, 'Завершить проект')

    def test_detail_shows_participate_for_non_owner(self):
        other = make_user(email='other@test.com', name='Другой', surname='Юзер')
        self.client.force_login(other)
        response = self.client.get(f'/projects/{self.project.id}')
        self.assertContains(response, 'Участвовать')


class CreateProjectTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_create_requires_login(self):
        response = self.client.get('/projects/create-project')
        self.assertRedirects(response, '/users/login/?next=/projects/create-project')

    def test_create_page_accessible(self):
        self.client.force_login(self.user)
        response = self.client.get('/projects/create-project')
        self.assertEqual(response.status_code, 200)

    def test_create_project(self):
        self.client.force_login(self.user)
        response = self.client.post('/projects/create-project', {
            'name': 'Новый проект', 'description': 'Описание', 'github_url': '', 'status': 'open',
        })
        project = Project.objects.get(name='Новый проект')
        self.assertRedirects(response, f'/projects/{project.id}')
        self.assertEqual(project.owner, self.user)

    def test_create_adds_owner_to_participants(self):
        self.client.force_login(self.user)
        self.client.post('/projects/create-project', {
            'name': 'Мой проект', 'description': '', 'github_url': '', 'status': 'open',
        })
        project = Project.objects.get(name='Мой проект')
        self.assertIn(self.user, project.participants.all())

    def test_create_project_name_required(self):
        self.client.force_login(self.user)
        response = self.client.post('/projects/create-project', {
            'name': '', 'description': 'Описание', 'github_url': '', 'status': 'open',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(description='Описание').exists())

    def test_github_url_must_be_github(self):
        self.client.force_login(self.user)
        response = self.client.post('/projects/create-project', {
            'name': 'Проект', 'description': '', 'github_url': 'https://gitlab.com/repo',
            'status': 'open',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(name='Проект').exists())


class EditProjectTest(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_edit_requires_login(self):
        response = self.client.get(f'/projects/{self.project.id}/edit')
        self.assertRedirects(response, f'/users/login/?next=/projects/{self.project.id}/edit')

    def test_edit_forbidden_for_non_owner(self):
        other = make_user(email='other@test.com', name='Другой', surname='Юзер')
        self.client.force_login(other)
        response = self.client.get(f'/projects/{self.project.id}/edit')
        self.assertEqual(response.status_code, 404)

    def test_edit_saves_changes(self):
        self.client.force_login(self.owner)
        response = self.client.post(f'/projects/{self.project.id}/edit', {
            'name': 'Обновлённое название', 'description': 'Новое описание',
            'github_url': '', 'status': 'open',
        })
        self.assertRedirects(response, f'/projects/{self.project.id}')
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Обновлённое название')


class CompleteProjectTest(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_complete_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            f'/projects/{self.project.id}/complete/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['project_status'], 'closed')
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'closed')

    def test_complete_already_closed(self):
        self.project.status = 'closed'
        self.project.save()
        self.client.force_login(self.owner)
        response = self.client.post(
            f'/projects/{self.project.id}/complete/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_complete_forbidden_for_non_owner(self):
        other = make_user(email='other@test.com', name='Другой', surname='Юзер')
        self.client.force_login(other)
        response = self.client.post(
            f'/projects/{self.project.id}/complete/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)

    def test_complete_requires_login(self):
        response = self.client.post(
            f'/projects/{self.project.id}/complete/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)


class ToggleParticipateTest(TestCase):
    def setUp(self):
        self.owner = make_user()
        self.participant = make_user(email='p@test.com', name='Участник', surname='Тестов')
        self.project = make_project(self.owner)

    def test_join_project(self):
        self.client.force_login(self.participant)
        response = self.client.post(
            f'/projects/{self.project.id}/toggle-participate/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['participant'])
        self.assertIn(self.participant, self.project.participants.all())

    def test_leave_project(self):
        self.project.participants.add(self.participant)
        self.client.force_login(self.participant)
        response = self.client.post(
            f'/projects/{self.project.id}/toggle-participate/',
            content_type='application/json',
        )
        data = response.json()
        self.assertFalse(data['participant'])
        self.assertNotIn(self.participant, self.project.participants.all())

    def test_owner_cannot_participate(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            f'/projects/{self.project.id}/toggle-participate/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_participate_requires_login(self):
        response = self.client.post(
            f'/projects/{self.project.id}/toggle-participate/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)
