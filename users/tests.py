import json

from django.test import TestCase

from .models import Skill, User


def make_user(email='test@test.com', name='Иван', surname='Иванов', password='testpass123'):
    return User.objects.create_user(email=email, name=name, surname=surname, password=password)


class RegistrationTest(TestCase):
    def test_register_page_accessible(self):
        response = self.client.get('/users/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post('/users/register/', {
            'name': 'Иван', 'surname': 'Иванов',
            'email': 'ivan@test.com', 'password': 'testpass123',
        })
        self.assertRedirects(response, '/users/login/')
        self.assertTrue(User.objects.filter(email='ivan@test.com').exists())

    def test_register_duplicate_email(self):
        make_user(email='ivan@test.com')
        response = self.client.post('/users/register/', {
            'name': 'Другой', 'surname': 'Иванов',
            'email': 'ivan@test.com', 'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='ivan@test.com').count(), 1)

    def test_register_redirect_if_authenticated(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get('/users/register/')
        self.assertRedirects(response, '/projects/list')


class LoginTest(TestCase):
    def setUp(self):
        self.user = make_user(email='ivan@test.com', password='testpass123')

    def test_login_page_accessible(self):
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/users/login/', {
            'email': 'ivan@test.com', 'password': 'testpass123',
        })
        self.assertRedirects(response, '/projects/list')

    def test_login_wrong_password(self):
        response = self.client.post('/users/login/', {
            'email': 'ivan@test.com', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.get('/users/logout/')
        self.assertRedirects(response, '/projects/list')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserDetailTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_profile_page_accessible(self):
        response = self.client.get(f'/users/{self.user.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.name)

    def test_profile_page_404_for_nonexistent(self):
        response = self.client.get('/users/99999/')
        self.assertEqual(response.status_code, 404)


class EditProfileTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_edit_profile_requires_login(self):
        response = self.client.get('/users/edit-profile/')
        self.assertRedirects(response, '/users/login/?next=/users/edit-profile/')

    def test_edit_profile_page_accessible(self):
        self.client.force_login(self.user)
        response = self.client.get('/users/edit-profile/')
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_saves(self):
        self.client.force_login(self.user)
        response = self.client.post('/users/edit-profile/', {
            'name': 'Пётр', 'surname': 'Иванов',
            'about': 'Python dev', 'phone': '', 'github_url': '',
        })
        self.assertRedirects(response, f'/users/{self.user.id}/')
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Пётр')


class ChangePasswordTest(TestCase):
    def setUp(self):
        self.user = make_user(password='oldpass123')

    def test_change_password_requires_login(self):
        response = self.client.get('/users/change-password/')
        self.assertRedirects(response, '/users/login/?next=/users/change-password/')

    def test_change_password_success(self):
        self.client.force_login(self.user)
        response = self.client.post('/users/change-password/', {
            'old_password': 'oldpass123',
            'new_password1': 'newpass456',
            'new_password2': 'newpass456',
        })
        self.assertRedirects(response, f'/users/{self.user.id}/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass456'))

    def test_change_password_wrong_old(self):
        self.client.force_login(self.user)
        response = self.client.post('/users/change-password/', {
            'old_password': 'wrongpass',
            'new_password1': 'newpass456',
            'new_password2': 'newpass456',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('oldpass123'))


class UserListTest(TestCase):
    def setUp(self):
        self.user1 = make_user(email='u1@test.com')
        self.user2 = make_user(email='u2@test.com', name='Анна', surname='Петрова')

    def test_list_accessible(self):
        response = self.client.get('/users/list')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.name)
        self.assertContains(response, self.user2.name)

    def test_filter_by_skill(self):
        skill = Skill.objects.create(name='Python')
        self.user1.skills.add(skill)
        response = self.client.get('/users/list?skill=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.name)
        self.assertNotContains(response, self.user2.name)

    def test_filter_nonexistent_skill_returns_empty(self):
        response = self.client.get('/users/list?skill=Nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.user1.name)


class SkillsAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        Skill.objects.create(name='Python')
        Skill.objects.create(name='Django')

    def test_autocomplete_returns_matches(self):
        self.client.force_login(self.user)
        response = self.client.get('/users/skills/?q=py')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [s['name'] for s in data]
        self.assertIn('Python', names)

    def test_add_skill_by_name(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f'/users/{self.user.id}/skills/add/',
            data=json.dumps({'name': 'Python'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(Skill.objects.get(name='Python'), self.user.skills.all())

    def test_add_skill_creates_new(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f'/users/{self.user.id}/skills/add/',
            data=json.dumps({'name': 'NewSkill'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Skill.objects.filter(name='NewSkill').exists())

    def test_remove_skill(self):
        self.client.force_login(self.user)
        skill = Skill.objects.get(name='Python')
        self.user.skills.add(skill)
        response = self.client.post(
            f'/users/{self.user.id}/skills/{skill.id}/remove/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(skill, self.user.skills.all())

    def test_add_skill_forbidden_for_other_user(self):
        other = make_user(email='other@test.com', name='Другой', surname='Юзер')
        self.client.force_login(other)
        response = self.client.post(
            f'/users/{self.user.id}/skills/add/',
            data=json.dumps({'name': 'Python'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
