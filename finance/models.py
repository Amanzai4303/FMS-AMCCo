from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from common.utils import gregorian_to_afghan_date

class Transaction(models.Model):
    TYPE_CHOICES = [('IN', 'Cash IN'), ('OUT', 'Cash OUT')]
    PAYMENT_METHODS = [('cash', 'Cash'), ('bank', 'Bank Transfer')]

    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    category = models.ForeignKey('expenses.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01, message="Amount must be positive.")])
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} ({self.project.code})"

    @property
    def date_afghan(self):
        return gregorian_to_afghan_date(self.date)

    def clean(self):
        if self.type == 'OUT' and not self.category:
            raise ValidationError({'category': 'Category is required for Cash OUT transactions.'})
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be a positive number.'})

class TransactionAttachment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='transaction_docs/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)