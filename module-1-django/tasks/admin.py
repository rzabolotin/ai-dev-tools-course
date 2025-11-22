from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'is_done', 'created_at')
    list_filter = ('is_done', 'user', 'due_date')
    search_fields = ('title', 'description')
    list_editable = ('is_done',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Status & Dates', {
            'fields': ('is_done', 'due_date', 'created_at')
        }),
    )
