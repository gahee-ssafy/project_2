from config.urls import path
from . import views

urlpatterns = [
    # fronted에서 요청을 받는 엔드포인트
    path('results/', views.receive_analysis),
    # FastAPI에서 콜백을 받을 엔드포인트
    path('callback/', views.receive_analysis_callback),
    # frontend에서 특정 파일명의 분석 결과를 요청하는 엔드포인트
    path('summaries/', views.get_analysis_result),
    # frontend에서 분석 결과 전체 리스트를 요청하는 엔드포인트
    path('list/', views.get_analysis_list),
]