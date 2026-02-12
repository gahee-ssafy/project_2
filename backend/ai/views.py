from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import httpx
from .models import AnalysisResult

# 프론트엔드의 요청을 받는 함수 
@csrf_exempt
def receive_analysis(request):
    """
    [통합 공정]
    1. 프론트엔드로부터 파일 내용 수신 (POST)
    2. FastAPI(9000)로 분석 요청 중계
    """
    if request.method == 'POST':
        # 1. 프론트엔드 데이터 추출
        data = json.loads(request.body)
        filename = data.get('filename')
        code_content = data.get('code_content')

            # FastAPI에게 "나중에 여기(Callback)로 결과 줘"라고 말하며 요청
        try:
            # 비동기적으로 쏘기 위해 timeout을 짧게 잡거나 그냥 던집니다.
            with httpx.Client() as client:
                client.post("http://127.0.0.1:9000/ai/analyze-file", json=data)
            
            # FastAPI의 응답을 기다리지 않고 즉시 프론트에 반환
            return JsonResponse({"status": "processing", "message": "분석이 시작되었습니다."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        """
        db에 저장을 안한다. 그대로 토스하는 형식인 거죠? 콜백을 받아서 내용이 중요하니까요. 
        굳이 저장을 하지 않는 것 같아요. 
        """

@csrf_exempt
def receive_analysis_callback(request):
    if request.method == 'POST':
        # 1. FastAPI에서 보낸 데이터 추출
        try: 
            data = json.loads(request.body)
            
        # 2. DB에 저장
            result = AnalysisResult.objects.create(
                filename=data.get('filename'),
                analysis=data.get('analysis'),
                code_content=data.get('code_content'), # 오타 수정 완료
                created_at=data.get('created_at') 
            )
        
            print(f"[DEBUG] 분석 결과 저장 완료: {result.filename}")
            return JsonResponse({"status": "success", "message": "분석 결과가 저장되었습니다."})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"message": "POST 요청만 가능합니다."}, status=405)

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

