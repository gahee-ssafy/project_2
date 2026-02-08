from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/files/', include('files.urls')), # 파일 관련 API
    path('api/git_app/', include('git_app.urls')), # 깃 관련 API
]



