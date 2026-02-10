from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AnalysisResult

@csrf_exempt # FastAPI(외부)에서 들어오는 요청의 보안 검사를 통과시키기 위함
def receive_analysis(request):
    """AI 서버로부터 분석 결과를 수신하는 엔드포인트"""
    if request.method == 'POST':
        try:
            # 전달받은 JSON 데이터 파싱
            data = json.loads(request.body)
            
            # DB에 데이터 생성 및 저장 (Create)
            new_result = AnalysisResult.objects.create(
                filename=data.get('filename'),
                analysis=data.get('analysis'),
                code_content=data.get('code_content', '') # FastAPI에서 보냈을 경우 저장
            )

            print(f"[DB SAVED] ID: {new_result.id} - {new_result.filename}")
            
            return JsonResponse({
                "status": "success", 
                "message": f"DB 저장 완료 (ID: {new_result.id})"
            }, status=200)

        except Exception as e:
            print(f"[DEBUG] 정체: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "fail"}, status=405)


def get_analysis_list(request):
    """DB에 저장된 모든 분석 결과를 프론트엔드로 전송"""
    if request.method == 'GET':
        # 1. DB에서 모든 데이터 조회
        results = AnalysisResult.objects.all().order_by('-created_at')
        
        # 2. 파이썬 객체를 JSON으로 변환 가능한 리스트로 가공
        data_list = []
        for res in results:
            data_list.append({
                "id": res.id,
                "filename": res.filename,
                "analysis": res.analysis,
                "created_at": res.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # 3. JSON으로 응답
        return JsonResponse({"results": data_list}, status=200)
    
    return JsonResponse({"message": "GET 요청만 가능합니다."}, status=405)