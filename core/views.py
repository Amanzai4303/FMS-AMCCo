# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from .models import (
    Project, ProjectDocument, Category,
    Transaction, TransactionAttachment
)
from .forms import ProjectForm, TransactionForm
from .utils import get_afghan_date


# ---------- HELPERS ----------
def is_admin(user):
    return user.is_superuser


# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    total_revenue = Transaction.objects.filter(type='IN').aggregate(
        total=Sum('amount'))['total'] or 0
    total_expenses = Transaction.objects.filter(type='OUT').aggregate(
        total=Sum('amount'))['total'] or 0

    all_projects = list(Project.objects.all())
    total_profit_loss = sum(p.profit_loss for p in all_projects)

    recent_txns = Transaction.objects.select_related('project', 'category') \
                       .order_by('-date', '-created_at')[:5]

    chart_projects = sorted(all_projects, key=lambda p: abs(p.profit_loss), reverse=True)[:5]
    chart_data = []
    for proj in chart_projects:
        budget = proj.budget if proj.budget > 0 else 1
        abs_pl = abs(proj.profit_loss)

        if proj.profit_loss >= 0:
            raw_width = (proj.profit_loss / budget) * 100
            bar_color = 'bg-success'
            text_color = 'text-success'
        else:
            raw_width = (abs_pl / budget) * 100
            bar_color = 'bg-danger'
            text_color = 'text-danger'

        bar_width = min(raw_width, 100)
        if abs_pl > 0 and bar_width < 2:
            bar_width = 2

        chart_data.append({
            'code': proj.code,
            'profit_loss': proj.profit_loss,
            'bar_width': bar_width,
            'bar_color': bar_color,
            'text_color': text_color,
        })

    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit_loss': total_profit_loss,
        'recent_txns': recent_txns,
        'chart_data': chart_data,
    }
    return render(request, 'dashboard.html', context)


# ========== PROJECTS ==========
@login_required
def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    documents = project.documents.all()
    expenses = project.transactions.filter(type='OUT').select_related('category')
    incomes = project.transactions.filter(type='IN')
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'documents': documents,
        'expenses': expenses,
        'incomes': incomes,
    })


@login_required
@user_passes_test(is_admin)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            files = request.FILES.getlist('documents')
            for f in files:
                ProjectDocument.objects.create(project=project, file=f, filename=f.name)
            messages.success(request, f'Project {project.code} created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            files = request.FILES.getlist('documents')
            for f in files:
                ProjectDocument.objects.create(project=project, file=f, filename=f.name)
            messages.success(request, f'Project {project.code} updated.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'action': 'Update'})


# ========== EXPENSES PAGE (Categorized) ==========
@login_required
def expense_list(request):
    project_id = request.GET.get('project')
    selected_project = None
    categories_totals = []
    total_expenses = 0

    if project_id:
        selected_project = get_object_or_404(Project, pk=project_id)
        out_txns = Transaction.objects.filter(
            project=selected_project, type='OUT'
        ).select_related('category').order_by('-date')

        total_expenses = out_txns.aggregate(total=Sum('amount'))['total'] or 0

        cat_map = {}
        for txn in out_txns:
            cat_name = txn.category.name if txn.category else 'Uncategorized'
            if cat_name not in cat_map:
                cat_map[cat_name] = {'transactions': [], 'total': 0}
            cat_map[cat_name]['transactions'].append(txn)
            cat_map[cat_name]['total'] += txn.amount

        for name, data in cat_map.items():
            categories_totals.append({
                'category': name,
                'total': data['total'],
                'transactions': data['transactions'],
            })

    projects = Project.objects.all()
    return render(request, 'transactions/expense_list.html', {
        'projects': projects,
        'selected_project': selected_project,
        'categories_totals': categories_totals,
        'total_expenses': total_expenses,
    })


# ========== CASH IN ==========
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
        form.fields.pop('category', None)  # remove category – not needed for Cash IN
    return render(request, 'transactions/cash_form.html', {
        'form': form,
        'action': 'Add Cash IN',
        'type': 'IN',
    })


@login_required
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


# ========== CASH OUT ==========
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


# ========== DELETE TRANSACTION (Admin only) ==========
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


# ========== REPORTS ==========
@login_required
def report_list(request):
    report_type = request.GET.get('type', 'list')
    project_id = request.GET.get('project')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    txn_type = request.GET.get('txn_type', '')

    projects = Project.objects.all()
    context = {
        'projects': projects,
        'report_type': report_type,
        'selected_project': None,
        'from_date': from_date,
        'to_date': to_date,
        'txn_type': txn_type,
    }

    if report_type == 'list':
        transactions = Transaction.objects.select_related('project', 'category', 'created_by').order_by('-date')
        if project_id:
            context['selected_project'] = get_object_or_404(Project, pk=project_id)
            transactions = transactions.filter(project_id=project_id)
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
        if txn_type in ('IN', 'OUT'):
            transactions = transactions.filter(type=txn_type)

        context['transactions'] = transactions
        context['total_income'] = transactions.filter(type='IN').aggregate(s=Sum('amount'))['s'] or 0
        context['total_expenses'] = transactions.filter(type='OUT').aggregate(s=Sum('amount'))['s'] or 0
        context['profit_loss'] = context['total_income'] - context['total_expenses']

    elif report_type == 'profit_loss':
        projects_qs = Project.objects.all()
        if project_id:
            context['selected_project'] = get_object_or_404(Project, pk=project_id)
            projects_qs = projects_qs.filter(pk=project_id)

        profit_data = []
        total_budget = total_income_all = total_expenses_all = 0
        for proj in projects_qs:
            # Start with all transactions for the project
            base_txns = proj.transactions.all()
            if from_date:
                base_txns = base_txns.filter(date__gte=from_date)
            if to_date:
                base_txns = base_txns.filter(date__lte=to_date)

            income = base_txns.filter(type='IN').aggregate(s=Sum('amount'))['s'] or 0
            expenses = base_txns.filter(type='OUT').aggregate(s=Sum('amount'))['s'] or 0
            profit_data.append({
                'code': proj.code,
                'name': proj.name,
                'budget': proj.budget,
                'income': income,
                'expenses': expenses,
                'profit_loss': income - expenses,
            })
            total_budget += proj.budget
            total_income_all += income
            total_expenses_all += expenses

        context['profit_loss_data'] = profit_data
        context['total_budget'] = total_budget
        context['total_income_all'] = total_income_all
        context['total_expenses_all'] = total_expenses_all
        context['net_all'] = total_income_all - total_expenses_all

    return render(request, 'reports/report_list.html', context)


@login_required
def report_pdf(request):
    report_type = request.GET.get('type', 'list')
    project_id = request.GET.get('project')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    txn_type = request.GET.get('txn_type', '')

    afghan_date_str = get_afghan_date()

    context = {
        'report_type': report_type,
        'report_title': 'Expenses & Incomes List' if report_type == 'list' else 'Project Profit / Loss Statement',
        'afghan_date': afghan_date_str,
    }

    if report_type == 'list':
        transactions = Transaction.objects.select_related('project', 'category', 'created_by').order_by('-date')
        if project_id:
            transactions = transactions.filter(project_id=project_id)
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
        if txn_type in ('IN', 'OUT'):
            transactions = transactions.filter(type=txn_type)

        context['transactions'] = transactions
        context['total_income'] = transactions.filter(type='IN').aggregate(s=Sum('amount'))['s'] or 0
        context['total_expenses'] = transactions.filter(type='OUT').aggregate(s=Sum('amount'))['s'] or 0
        context['profit_loss'] = context['total_income'] - context['total_expenses']

    elif report_type == 'profit_loss':
        projects_qs = Project.objects.all()
        if project_id:
            projects_qs = projects_qs.filter(pk=project_id)

        profit_data = []
        total_budget = total_income_all = total_expenses_all = 0
        for proj in projects_qs:
            income = proj.transactions.filter(type='IN').aggregate(s=Sum('amount'))['s'] or 0
            expenses = proj.transactions.filter(type='OUT').aggregate(s=Sum('amount'))['s'] or 0
            profit_data.append({
                'code': proj.code,
                'name': proj.name,
                'budget': proj.budget,
                'income': income,
                'expenses': expenses,
                'profit_loss': income - expenses,  # FIXED
            })
            total_budget += proj.budget
            total_income_all += income
            total_expenses_all += expenses

        context['profit_loss_data'] = profit_data
        context['total_budget'] = total_budget
        context['total_income_all'] = total_income_all
        context['total_expenses_all'] = total_expenses_all
        context['net_all'] = total_income_all - total_expenses_all  # FIXED

    html_string = render_to_string('reports/pdf_report.html', context)
    response = HttpResponse(content_type='application/pdf')
    filename = f"AMCC_Report_{report_type}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response