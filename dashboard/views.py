# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from projects.models import Project
from finance.models import Transaction

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

    # Filter for active and on_hold projects only
    chart_projects = [
        p for p in all_projects
        if p.status in ('active', 'on_hold')
    ]
    # Keep the top 5 by absolute profit/loss
    chart_projects = sorted(chart_projects, key=lambda p: abs(p.profit_loss), reverse=True)[:5]

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