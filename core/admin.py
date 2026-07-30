from django.contrib import admin
from .models import Project, ProjectDocument
from .models import Category, Transaction, TransactionAttachment

class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'client_name', 'budget', 'status', 'start_date', 'end_date']
    list_filter = ['status']
    search_fields = ['code', 'name', 'client_name']
    inlines = [ProjectDocumentInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']

class TransactionAttachmentInline(admin.TabularInline):
    model = TransactionAttachment
    extra = 1

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'type', 'category', 'amount', 'date', 'payment_method']
    list_filter = ['type', 'payment_method', 'date']
    search_fields = ['description', 'project__name']
    inlines = [TransactionAttachmentInline]