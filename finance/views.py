# finance/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from common.utils import is_admin
from .models import Transaction, TransactionAttachment
from .forms import TransactionForm
from projects.models import Project
from common.utils import is_admin

@login_required
def cashin_list(request):
    project_id = request.GET.get('project')
    selected_project = None
    txns = Transaction.objects.filter(type='IN').select_related('project')
    if project_id:
        selected_project = get_object_or_404(Project, pk=project_id)
        txns = txns.filter(project=selected_project)
    projects = Project.objects.all()
    return render(request, 'transactions/cashin_list.html', {
        'txns': txns.order_by('-date'),
        'projects': projects,
        'selected_project': selected_project,
    })

@login_required
def cashin_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.type = 'IN'
            txn.created_by = request.user
            txn.full_clean()
            txn.save()
            files = request.FILES.getlist('attachments')
            for f in files:
                TransactionAttachment.objects.create(transaction=txn, file=f, filename=f.name)
            messages.success(request, 'Cash IN recorded.')
            return redirect('cashin_list')
    else:
        form = TransactionForm(initial={'type': 'IN'})
        form.fields.pop('category', None)
    return render(request, 'transactions/cash_form.html', {
        'form': form,
        'action': 'Add Cash IN',
        'type': 'IN',
    })

@login_required
@user_passes_test(is_admin)
def cashin_edit(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, type='IN')
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.type = 'IN'
            txn.full_clean()
            txn.save()
            files = request.FILES.getlist('attachments')
            for f in files:
                TransactionAttachment.objects.create(transaction=txn, file=f, filename=f.name)
            messages.success(request, 'Cash IN updated.')
            return redirect('cashin_list')
    else:
        form = TransactionForm(instance=txn)
        form.fields.pop('category', None)
    return render(request, 'transactions/cash_form.html', {
        'form': form,
        'action': 'Edit Cash IN',
        'type': 'IN',
    })

@login_required
def cashout_list(request):
    project_id = request.GET.get('project')
    selected_project = None
    txns = Transaction.objects.filter(type='OUT').select_related('project', 'category')
    if project_id:
        selected_project = get_object_or_404(Project, pk=project_id)
        txns = txns.filter(project=selected_project)
    projects = Project.objects.all()
    return render(request, 'transactions/cashout_list.html', {
        'txns': txns.order_by('-date'),
        'projects': projects,
        'selected_project': selected_project,
    })

@login_required
def cashout_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.type = 'OUT'
            txn.created_by = request.user
            txn.full_clean()
            txn.save()
            files = request.FILES.getlist('attachments')
            for f in files:
                TransactionAttachment.objects.create(transaction=txn, file=f, filename=f.name)
            messages.success(request, 'Cash OUT recorded.')
            return redirect('cashout_list')
    else:
        form = TransactionForm(initial={'type': 'OUT'})
    return render(request, 'transactions/cash_form.html', {
        'form': form,
        'action': 'Add Cash OUT',
        'type': 'OUT',
    })

@login_required
@user_passes_test(is_admin)
def cashout_edit(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, type='OUT')
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.type = 'OUT'
            txn.full_clean()
            txn.save()
            files = request.FILES.getlist('attachments')
            for f in files:
                TransactionAttachment.objects.create(transaction=txn, file=f, filename=f.name)
            messages.success(request, 'Cash OUT updated.')
            return redirect('cashout_list')
    else:
        form = TransactionForm(instance=txn)
    return render(request, 'transactions/cash_form.html', {
        'form': form,
        'action': 'Edit Cash OUT',
        'type': 'OUT',
    })

@login_required
@user_passes_test(is_admin)
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        txn_type = txn.type
        txn.delete()
        messages.success(request, 'Transaction deleted.')
        if txn_type == 'IN':
            return redirect('cashin_list')
        return redirect('cashout_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'txn': txn})