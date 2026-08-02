from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from common.utils import gregorian_to_afghan_date

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    location = models.CharField(max_length=300)
    client_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='projects_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_expenses(self):
        from django.db.models import Sum
        return self.transactions.filter(type='OUT').aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_income(self):
        from django.db.models import Sum
        return self.transactions.filter(type='IN').aggregate(total=Sum('amount'))['total'] or 0

    @property
    def profit_loss(self):
        return self.total_income - self.total_expenses

    @property
    def start_date_afghan(self):
        return gregorian_to_afghan_date(self.start_date)

    @property
    def end_date_afghan(self):
        return gregorian_to_afghan_date(self.end_date)

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before start date.'})

class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='project_docs/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.code} - {self.filename}"