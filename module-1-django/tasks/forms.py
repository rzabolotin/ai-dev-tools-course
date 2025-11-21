from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control bg-light border-0 focus:ring-2 focus:ring-indigo-500 transition-all'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg bg-light border-0 focus:ring-2 focus:ring-indigo-500 transition-all', 
                'placeholder': 'What needs to be done?'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control bg-light border-0 focus:ring-2 focus:ring-indigo-500 transition-all', 
                'rows': 4, 
                'placeholder': 'Add details...'
            }),
        }
