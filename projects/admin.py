from django.contrib import admin
from .models import Project, ProjectDocument

class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'client_name', 'budget', 'status', 'start_date', 'end_date']
    list_filter = ['status']
    search_fields = ['code', 'name', 'client_name']
    inlines = [ProjectDocumentInline]