from django.urls import path
from . import views

urlpatterns = [
    path('register/applicant/', views.register_applicant, name='register_applicant'),
    path('register/employer/', views.register_employer, name='register_employer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]