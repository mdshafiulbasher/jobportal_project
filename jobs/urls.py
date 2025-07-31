from django.urls import path
from . import views

urlpatterns = [
    # Employer URLs
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/post-job/', views.post_job, name='post_job'),
    path('employer/job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),

    # Applicant URLs
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
]