import os
from git import Repo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# files 앱에서 설정한 경로를 가져오기 위한 임포트
from files.views import current_context

@api_view(['GET'])
def git_status(request):
    """
    현재 프로젝트의 Git 상태(브랜치명, 변경된 파일 등)를 반환합니다.
    """
    root_path = current_context.get("root_path")
    if not root_path:
        return Response({"error": "먼저 프로젝트 경로를 설정해야 합니다."}, status=400)

    try:
        repo = Repo(root_path)
        return Response({
            "branch": repo.active_branch.name,
            "is_dirty": repo.is_dirty(), # 변경 사항 유무
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)]
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def git_commit_push(request):
    """
    변경 사항을 에드그리고 커밋하고 푸시합니다.
    """
    root_path = current_context.get("root_path")
    message = request.data.get('message', 'Auto-commit by Codin-Nator')

    if not root_path:
        return Response({"error": "경로 정보가 없습니다."}, status=400)

    try:
        repo = Repo(root_path)
        
        # 1. Add (모든 변경사항 스테이징)
        repo.git.add(A=True)
        
        # 2. Commit
        repo.index.commit(message)
        
        # 3. Push (원격 저장소 'origin' 기준)
        origin = repo.remote(name='origin')
        origin.push()
        
        return Response({"message": "커밋 및 푸시 성공"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)