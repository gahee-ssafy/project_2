from config.urls import path
from . import views

urlpatterns = [
    # FastAPI에서 DJANGO_URL로 설정한 경로와 일치해야 함
    path('results/', views.receive_analysis),
    # frontend에서 분석 결과 리스트를 요청하는 엔드포인트
    path('list/', views.get_analysis_list),
]