from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ApplicantRegistrationForm, EmployerRegistrationForm # We'll define these custom forms

def register_applicant(request):
    """
    Handles applicant registration.
    """
    if request.method == 'POST':
        form = ApplicantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = 'applicant' # Set user type
            user.save()
            login(request, user)
            messages.success(request, "Applicant account created successfully!")
            return redirect('applicant_dashboard')
    else:
        form = ApplicantRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register as Applicant'})

def register_employer(request):
    """
    Handles employer registration.
    """
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = 'employer' # Set user type
            user.save()
            login(request, user)
            messages.success(request, "Employer account created successfully!")
            return redirect('employer_dashboard')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register as Employer'})

def login_view(request):
    """
    Handles user login and redirects based on user type.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                if user.is_employer():
                    return redirect('employer_dashboard')
                else: # Default to applicant dashboard for non-employers
                    return redirect('applicant_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login') # Redirect to the login page