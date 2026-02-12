from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File

from google import genai
import chromadb
import os
from datetime import datetime
# chromadb로 시도하려 했으나, 라이브러리 충돌로 인한 문제로 json으로 시도. 
# json은 영구저장이 안되므로, 추후 고민사항

load_dotenv()
app = FastAPI()

# 엔진 초기화
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(
    name="code_analysis_collection",
    embedding_function=None) # 임베딩 함수는 나중에 설정 가능

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

        collection.upsert(
            documents=[code_text],
            metadatas=[{
                "filename": file.filename,
                "analysis": analysis_result[:100], # 분석 결과의 앞 100자만 메타데이터에 저장
                "timestamp": current_time
            }],
            embeddings=[[0.0] * 10],
            ids=[file.filename]
        )
        print(f"[DEBUG] ChromaDB 저장 성공")

        return {
            "status": "success",
            "filename": file.filename,
            "analysis": analysis_result
        }

    except Exception as e:
        # 에러 발생 시 구체적인 타입과 메시지를 터미널에 출력
        print(f"[CRITICAL ERROR] 타입: {type(e).__name__}")
        print(f"[CRITICAL ERROR] 내용: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 분석 실패: {str(e)}")