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
@user_passes_test(is_employer, login_url='login') # Redirect to login if not employer
def employer_dashboard(request):
    """
    Displays jobs posted by the current employer.
    """
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    return render(request, 'jobs/employer_dashboard.html', {'jobs': jobs})

@login_required
@user_passes_test(is_employer, login_url='login')
def post_job(request):
    """
    Allows an employer to post a new job.
    """
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
    Displays a list of applicants for a specific job posted by the current employer.
    """
    job = get_object_or_404(Job, id=job_id, posted_by=request.user) # Ensure only their jobs
    applications = job.applications.all().select_related('applicant').order_by('-applied_at') # Optimize with select_related
    return render(request, 'jobs/job_applicants.html', {'job': job, 'applications': applications})

# --- Applicant Functionalities ---

@login_required
@user_passes_test(is_applicant, login_url='login')
def applicant_dashboard(request):
    """
    Displays jobs the current applicant has applied for.
    """
    applications = Application.objects.filter(applicant=request.user).select_related('job').order_by('-applied_at')
    return render(request, 'jobs/applicant_dashboard.html', {'applications': applications})

@login_required # Jobs can be viewed by anyone logged in, but apply only by applicant
def job_list(request):
    """
    Displays a list of all available jobs with search functionality.
    """
    jobs = Job.objects.all().order_by('-created_at')
    query = request.GET.get('q') # Get the search query from the URL parameter 'q'

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |        # Case-insensitive contains for title
            Q(company_name__icontains=query) | # Case-insensitive contains for company_name
            Q(location__icontains=query)       # Case-insensitive contains for location
        ).distinct() # Use .distinct() to avoid duplicate results if a job matches multiple criteria
    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'query': query})

@login_required
def job_detail(request, job_id):
    """
    Displays details of a specific job.
    Also checks if the current user (if applicant) has already applied.
    """
    job = get_object_or_404(Job, id=job_id)
    has_applied = False
    if request.user.is_authenticated and request.user.is_applicant():
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
@user_passes_test(is_applicant, login_url='login')
def apply_job(request, job_id):
    """
    Allows an applicant to apply for a job.
    """
    job = get_object_or_404(Job, id=job_id)

    # Prevent multiple applications for the same job by the same applicant
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