# core/forms.py
from django import forms
from .models import Project, Transaction, Category


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


class TransactionForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label='Category'
    )

    class Meta:
        model = Transaction
        fields = [
            'project', 'type', 'category', 'amount', 'date',
            'payment_method', 'description'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'AFN amount'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If creating a new Cash OUT (initial dict has type='OUT')
        if kwargs.get('initial', {}).get('type') == 'OUT':
            self.fields['category'].required = True
        # If editing an existing Cash OUT transaction
        if self.instance and self.instance.pk and self.instance.type == 'OUT':
            self.fields['category'].required = True