from django.db import models

class AnalysisResult(models.Model):
    # 파일명 저장
    filename = models.CharField(max_length=255)
    # 분석 결과 (긴 텍스트이므로 TextField 사용)
    analysis = models.TextField()
    # 원본 코드 내용 (나중에 다시 볼 수 있게 저장)
    code_content = models.TextField(blank=True, null=True)
    # 생성 시각 (자동 기록)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.created_at}"