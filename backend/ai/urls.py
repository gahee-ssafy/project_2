from config.urls import path
from . import views

urlpatterns = [
    # FastAPI에서 DJANGO_URL로 설정한 경로와 일치해야 함
    path('results/', views.receive_analysis),
]