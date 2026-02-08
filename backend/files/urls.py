from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.file_list),      # GET /api/files/list/
    path('detail/', views.file_detail),  # POST /api/files/detail/
    path('save/', views.file_save),      # POST /api/files/save/
]