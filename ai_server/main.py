from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from google import genai

# import chromadb
import json
import os
from datetime import datetime

# 통신
import httpx

load_dotenv()
app = FastAPI()
# [중요] API 주소 
DJANGO_URL = "http://127.0.0.1:8000/api/ai/results/"

# 엔진 초기화
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 저장 폴더 경로 설정 (없으면 생성)
SAVE_DIR = "analysis_results"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)



@app.post("/ai/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        # [Step 1] 파일 내용 읽기
        print(f"[DEBUG] 수신된 파일명: {file.filename}") # 파일 도달 확인
        content = await file.read()
        code_text = content.decode("utf-8")
        print(f"[DEBUG] 파일 내용 일부(50자): {code_text[:50]}...") # 디코딩 성공 확인

        # [Step 2] Gemini AI에게 파일 내용 전달 및 분석
        print(f"[DEBUG] Gemini API 호출 시도...")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"다음 파일({file.filename})의 소스 코드를 분석해줘:\n\n{code_text}"
        )
        analysis_result = response.text
        print(f"[DEBUG] Gemini 분석 결과 수신 완료 (길이: {len(analysis_result)}자)")

        ####################################################
        # [Step 3] ChromaDB에 파일 내용과 분석 결과 적재
        print(f"[DEBUG] ChromaDB 데이터 적재 시도...")
        # 현재 시각을 YYYY-MM-DD HH:MM:SS 형식으로 추출
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[DEBUG] 3-1: 타임스탬프 생성 완료 ({current_time})")

        # ID 값 검증 로직 추가
        safe_id = str(file.filename).strip().replace(" ", "_")
        print(f"[DEBUG] 3-2: 준비된 ID값 확인: '{safe_id}'")

        # 저장할 데이터 구조화
        data_to_save = {
            "filename": file.filename,
            "analysis": analysis_result,
            "code_content": code_text,
            "timestamp": current_time
        }
        
        # Django로 데이터 전송
        await send_to_django(data_to_save) 


        # 파일명에서 공백 및 특수문자 치환 (안전한 파일명 생성)
        safe_filename = file.filename.replace(" ", "_").replace("/", "_")
        json_file_path = os.path.join(SAVE_DIR, f"{safe_filename}.json")

        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            
        print(f"[DEBUG] JSON 저장 성공: {json_file_path}")

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": analysis_result,
            "saved_at": json_file_path
        }

    except Exception as e:
        print(f"[CRITICAL ERROR] 타입: {type(e).__name__}")
        print(f"[CRITICAL ERROR] 내용: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 분석 실패: {str(e)}")
    
@app.get("/ai/results")
async def list_results():
    files = os.listdir(SAVE_DIR)
    return {"results": [f.replace(".json", "") for f in files if f.endswith(".json")]}


async def send_to_django(payload: dict):
    """Django 백엔드로 데이터를 전송하는 서브 공정"""
    async with httpx.AsyncClient() as client:
        try:
            print(f"[DEBUG] Django로 데이터 전송 시도: {DJANGO_URL}")
            response = await client.post(DJANGO_URL, json=payload, timeout=10.0)
            
            if response.status_code == 200:
                print(f"[DEBUG] Django 전송 성공: {response.json()}")
            else:
                print(f"[WARNING] Django 응답 에러: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Django 서버가 꺼져있거나 통신 불가: {str(e)}")
