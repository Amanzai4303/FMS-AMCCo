# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from common.utils import is_admin
from .models import Project, ProjectDocument
from .forms import ProjectForm

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