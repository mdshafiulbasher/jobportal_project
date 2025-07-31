from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Job model.
    """
    list_display = ('title', 'company_name', 'location', 'posted_by', 'created_at')
    search_fields = ('title', 'company_name', 'location', 'description')
    list_filter = ('location', 'created_at', 'posted_by__user_type') # Filter by user type of the poster
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Application model.
    """
    list_display = ('job', 'applicant', 'applied_at', 'get_job_title', 'get_company_name', 'get_applicant_username')
    search_fields = ('job__title', 'job__company_name', 'applicant__username', 'cover_letter')
    list_filter = ('applied_at', 'job__location')
    date_hierarchy = 'applied_at'
    ordering = ('-applied_at',)

    # Custom methods to display related model fields in the list_display
    def get_job_title(self, obj):
        return obj.job.title
    get_job_title.short_description = 'Job Title'
    get_job_title.admin_order_field = 'job__title' # Allows sorting in admin by job title

    def get_company_name(self, obj):
        return obj.job.company_name
    get_company_name.short_description = 'Company'
    get_company_name.admin_order_field = 'job__company_name'

    def get_applicant_username(self, obj):
        return obj.applicant.username
    get_applicant_username.short_description = 'Applicant Username'
    get_applicant_username.admin_order_field = 'applicant__username'