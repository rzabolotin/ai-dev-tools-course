from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task
from .forms import TaskForm

class TaskFormTest(TestCase):
    def test_valid_form(self):
        data = {'title': 'Test Task', 'description': 'Test Description', 'due_date': '2023-12-31'}
        form = TaskForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'title': '', 'description': 'Test Description'}
        form = TaskForm(data=data)
        self.assertFalse(form.is_valid())

class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_task_create_view(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'New Description',
            'due_date': '2023-12-31'
        })
        self.assertEqual(response.status_code, 302) # Redirects to task_list
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_task_create_view_invalid(self):
        response = self.client.post(reverse('task_create'), {
            'title': '',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 200) # Renders form again
        self.assertFalse(Task.objects.filter(description='New Description').exists())
