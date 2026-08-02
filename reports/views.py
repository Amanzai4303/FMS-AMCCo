# reports/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from projects.models import Project
from finance.models import Transaction
from common.utils import get_afghan_date

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

    html_string = render_to_string('reports/pdf_report.html', context)
    response = HttpResponse(content_type='application/pdf')
    filename = f"AMCC_Report_{report_type}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')
    return response