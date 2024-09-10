from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Todo
from .forms import TodoForm

class TodoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.todo = Todo.objects.create(title='Test Todo', description='This is a test', user=self.user)

    def test_todo_creation(self):
        todo = Todo.objects.get(id=self.todo.pk)
        self.assertEqual(todo.title, self.todo.title)

class TodoViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.todo = Todo.objects.create(title='Test Todo', description='This is a test', user=self.user)

    def test_todo_list_view(self):
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')

    def test_todo_detail_view(self):
        response = self.client.get(reverse('todo_detail', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')

    def test_todo_create_view(self):
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Todo',
            'description': 'A new test todo',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())

    def test_todo_update_view(self):
        response = self.client.post(reverse('todo_update', args=[self.todo.pk]), {
            'title': 'Updated Todo',
            'description': 'An updated test todo',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Todo')

    def test_todo_delete_view(self):
        response = self.client.post(reverse('todo_delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after POST
        self.assertFalse(Todo.objects.filter(id=self.todo.pk).exists())

class TodoFormTest(TestCase):
    def test_valid_form(self):
        form = TodoForm(data={
            'title': 'Test Todo',
            'description': 'This is a test',
            'completed': False
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = TodoForm(data={
            'title': '',
            'description': 'This is a test',
            'completed': False
        })
        self.assertFalse(form.is_valid())

class AuthorizationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.todo = Todo.objects.create(title='User1 Todo', description='This is user1\'s todo', user=self.user1)

    def test_user_can_view_own_todo(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get(reverse('todo_detail', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_view_others_todo(self):
        self.client.login(username='user2', password='12345')
        response = self.client.get(reverse('todo_detail', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden