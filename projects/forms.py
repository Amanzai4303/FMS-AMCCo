# projects/forms.py
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'budget', 'location', 'client_name',
            'start_date', 'end_date', 'status', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kabul Tower'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., AMCC-001'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'AFN amount'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kabul, District 10'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Ministry of Urban Development'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }