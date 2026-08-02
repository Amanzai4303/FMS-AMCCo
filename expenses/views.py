# expenses/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from projects.models import Project
from finance.models import Transaction

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