from django.db import models
from django.conf import settings # To refer to AUTH_USER_MODEL

class Job(models.Model):
    """
    Model for job postings.
    """
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

class Application(models.Model):
    """
    Model for job applications.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='my_applications')
    resume = models.FileField(upload_to='resumes/') # Files will be saved in media/resumes/
    cover_letter = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure an applicant can only apply once to a specific job
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at'] # Order by most recent application first

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.username}"