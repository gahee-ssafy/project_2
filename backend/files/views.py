import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# 1. 함수 밖에서 공통 경로 관리 (서버 메모리에 상주)
# 실시간으로 프론트에서 주는 경로를 여기에 저장합니다.
current_context = {
    "root_path": None
}

@api_view(['POST']) # GET 대신 POST 권장 (경로 데이터를 body로 받기 위함)
def file_list(request):
    """
    프론트에서 준 root_path를 전역 변수에 저장하고 파일 목록을 반환합니다.
    """
    root_path = request.data.get('root_path')

    if not root_path or not os.path.exists(root_path):
        return Response({"error": "유효하지 않은 경로입니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. 외부 변수 업데이트
    current_context["root_path"] = root_path
    
    file_tree = []
    try:
        # node_modules 등 무거운 폴더는 탐색 제외 권장
        exclude = {'.git', 'venv', '__pycache__', 'node_modules'}
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in exclude]
            
            relative_path = os.path.relpath(root, root_path)
            file_tree.append({
                "directory": relative_path if relative_path != "." else "root",
                "folders": dirs,
                "files": files
            })
        return Response(file_tree, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def file_detail(request):
    """
    저장된 root_path를 기반으로 특정 파일 내용을 읽어옵니다.
    """
    root_path = current_context["root_path"]
    if not root_path:
        return Response({"error": "먼저 프로젝트 경로를 설정해야 합니다."}, status=400)

    file_path = request.data.get('path')
    full_path = os.path.join(root_path, file_path)

    if not os.path.exists(full_path):
        return Response({"error": f"파일을 찾을 수 없습니다: {full_path}"}, status=status.HTTP_404_NOT_FOUND)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response({"content": content}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def file_save(request):
    """
    저장된 root_path를 기반으로 수정된 내용을 저장합니다.
    """
    root_path = current_context["root_path"]
    if not root_path:
        return Response({"error": "경로 정보가 없습니다."}, status=400)

    file_path = request.data.get('path')
    content = request.data.get('content')
    full_path = os.path.join(root_path, file_path)

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return Response({"message": "저장 성공"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    