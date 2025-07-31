from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import ModelForm
from django import forms
from django.contrib import messages
from django.db.models import Q # For complex queries like search
from .models import Job, Application

# --- Custom Decorators for Role-Based Access ---
def is_employer(user):
    return user.is_authenticated and user.is_employer()

def is_applicant(user):
    return user.is_authenticated and user.is_applicant()

# --- Forms ---
class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company_name', 'location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 8}),
        }

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 8}),
        }

# --- Employer Functionalities ---

@login_required
@user_passes_test(is_employer, login_url='login')
def employer_dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
@user_passes_test(is_employer, login_url='login')
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('employer_dashboard')
    else:
        form = JobForm()
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
@user_passes_test(is_employer, login_url='login')
def job_applicants(request, job_id):
    """
    Displays a list of applicants for a specific job and handles status updates.
    """
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)

    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        try:
            application = job.applications.get(id=application_id)
            if new_status in ['Approved', 'Rejected']:
                application.status = new_status
                application.save()
                messages.success(request, f"Application for {application.applicant.username} has been {new_status.lower()}.")
            else:
                messages.error(request, "Invalid status update.")
        except Application.DoesNotExist:
            messages.error(request, "Application not found.")
        return redirect('job_applicants', job_id=job.id)

    applications = job.applications.all().select_related('applicant').order_by('-applied_at')
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applications': applications})

# --- Applicant Functionalities ---

@login_required
@user_passes_test(is_applicant, login_url='login')
def applicant_dashboard(request):
    """
    Displays applications submitted by the current applicant, with filtering by status.
    """
    status_filter = request.GET.get('status', 'All') # Default to 'All'
    applications = Application.objects.filter(applicant=request.user).select_related('job')

    if status_filter != 'All' and status_filter in [c[0] for c in Application.STATUS_CHOICES]:
        applications = applications.filter(status=status_filter)

    applications = applications.order_by('-applied_at')
    
    return render(request, 'jobs/applicant_dashboard.html', {'applications': applications, 'status_filter': status_filter})

@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    query = request.GET.get('q')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        ).distinct()
    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'query': query})

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    has_applied = False
    if request.user.is_authenticated and request.user.is_applicant():
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
@user_passes_test(is_applicant, login_url='login')
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('applicant_dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})