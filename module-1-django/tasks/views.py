from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .models import Task, Category
from .forms import TaskForm, CategoryForm


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)

    # Search
    search = request.GET.get('search', '')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Filter by status
    status = request.GET.get('status', '')
    if status == 'done':
        tasks = tasks.filter(is_done=True)
    elif status == 'pending':
        tasks = tasks.filter(is_done=False)

    # Filter by priority
    priority = request.GET.get('priority', '')
    if priority in ['low', 'medium', 'high']:
        tasks = tasks.filter(priority=priority)

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        tasks = tasks.filter(categories__id=category_id)

    # Filter by due date
    due_filter = request.GET.get('due', '')
    if due_filter == 'overdue':
        from django.utils import timezone
        tasks = tasks.filter(due_date__lt=timezone.now().date(), is_done=False)
    elif due_filter == 'today':
        from django.utils import timezone
        tasks = tasks.filter(due_date=timezone.now().date())
    elif due_filter == 'upcoming':
        from django.utils import timezone
        tasks = tasks.filter(due_date__gt=timezone.now().date())

    context = {
        'tasks': tasks,
        'categories': categories,
        'search': search,
        'status': status,
        'priority': priority,
        'category_id': category_id,
        'due_filter': due_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Task created successfully.')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_done = not task.is_done
    task.save()
    status = "completed" if task.is_done else "marked as incomplete"
    messages.success(request, f'Task {status}.')
    return redirect('task_list')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('task_list')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'tasks/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'tasks/category_list.html', {
        'categories': categories,
        'form': form
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category_list')

    return render(request, 'tasks/category_confirm_delete.html', {'category': category})
