from django.contrib import admin
from .models import Transaction, TransactionAttachment

class TransactionAttachmentInline(admin.TabularInline):
    model = TransactionAttachment
    extra = 1

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'type', 'category', 'amount', 'date', 'payment_method']
    list_filter = ['type', 'payment_method', 'date']
    search_fields = ['description', 'project__name']
    inlines = [TransactionAttachmentInline]