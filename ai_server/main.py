from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from google import genai

# import chromadb
import json
import os
from datetime import datetime

# 통신
import httpx

load_dotenv()
app = FastAPI()
# 엔진 초기화
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 저장 폴더 경로 설정 (없으면 생성)
SAVE_DIR = "analysis_results"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


# 비동기 처리 엔드포인트
@app.post("/ai/analyze-file")
async def analyze_file(data: dict, background_tasks: BackgroundTasks):
    try:
        filename = data.get("filename")
        code_content = data.get("code_content")
        background_tasks.add_task(perform_ai_process, filename, code_content)

        return {"status": "started"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요청 수신 실패: {str(e)}")
    
# AI 처리 함수
async def perform_ai_process(filename: str, code_content: str):
    try:
        # [Step 1] Gemini AI에게 파일 내용 전달 및 분석
        print(f"[DEBUG] Gemini API 호출 시도...")

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            # [TODO] 프롬프팅 수정 예정
            contents=f"다음 파일({filename})의 소스 코드를 분석해줘:\n\n{code_content}"
        )

        analysis_result = response.text
        print(f"[DEBUG] Gemini 분석 결과 수신 완료 (길이: {len(analysis_result)}자)")
        # [TODO] ChromaDB에 파일 내용과 분석 결과 적재
 
        # [Step 2] django 서버에 콜백 전송
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await send_to_django_callback({
            "filename": filename,
            "analysis": analysis_result,
            "code_content": code_content,
            "timestamp": current_time
        })
        
    except Exception as e:
        print(f"[BACKGROUND ERROR] {str(e)}")

    
@app.get("/ai/results")
async def list_results():
    files = os.listdir(SAVE_DIR)
    return {"results": [f.replace(".json", "") for f in files if f.endswith(".json")]}

# Django 콜백 전송 함수
async def send_to_django_callback(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:8000/api/ai/callback/", json=payload, timeout=10.0)
            print(f"[DEBUG] Django 응답 상태: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Django 서빙 실패: {str(e)}")
