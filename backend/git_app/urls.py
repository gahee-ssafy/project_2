from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.git_status),      # GET /api/git/status/
    path('commit/', views.git_commit_push), # POST /api/git/commit/
]