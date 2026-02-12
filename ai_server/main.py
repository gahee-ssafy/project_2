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

def build_analysis_prompt(filename, code_content):
    return f"""
## [시스템 역할]
당신은 분산 아키텍처 환경의 AI 분석 엔진입니다. 당신의 목적은 소스 코드를 분석하여 '사과(데이터)'를 생성하고, 이를 비동기 콜백 선로를 통해 Django '바구니(DB)'에 적재하는 것입니다.

## [워크플로우 및 통신 규약]
1. 분석: 코드의 구조와 비동기 통신 적합성을 검토합니다.
2. 전송: 분석 결과는 POST /api/ai/callback/ 엔드포인트를 통해 전달됩니다.
3. 조회: 사용자는 GET /api/ai/result/에서 당신의 결과를 폴링합니다.

## [입출력 예시 (Few-shot)]
### 예시 1
**입력**: public void save() {{ repository.save(data); }}
**출력**:
[분석 결과: 저장 로직]
- 구조 분석: 표준적인 JPA 저장 방식입니다.
- 통신 관점: 이 데이터는 현재 /callback 경로를 통해 DB 바구니로 이동할 준비가 되었습니다.

### 예시 2
**입력**: @GetMapping("/status") public String getStatus() {{ return "OK"; }}
**출력**:
[분석 결과: 상태 확인 엔드포인트]
- 구조 분석: 단순 상태 반환 컨트롤러입니다.
- 통신 관점: /result 창구에서 수행하는 폴링 메커니즘과 유사한 단순 조회 로직입니다.

## [실제 분석 작업 시작]
**파일명**: {filename}
**소스 코드**:
{code_content}

## [최종 지시]
1. 위 예시의 [분석 결과] 형식을 엄격히 준수하십시오.
2. 서론, 결론, 가이드라인 복사 없이 오직 '분석 결과' 텍스트만 출력하십시오.
3. 분석 결과는 즉시 /callback 엔드포인트로 전송될 것이므로 데이터의 무결성을 유지하십시오.
"""

# AI 처리 함수
async def perform_ai_process(filename: str, code_content: str):
    try:
        # [Step 1] 프롬프트 빌드-LLM 호출-수신
        prompt = build_analysis_prompt(filename, code_content)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt)
        
        analysis_result = response.text

        print(f"[DEBUG] Gemini 분석 결과 수신 완료 (길이: {len(analysis_result)}자)")
        # [TODO] ChromaDB에 파일 내용과 분석 결과 적재
 
        # [Step 2] django 서버에 콜백 전송
        await send_to_django_callback({
            "filename": filename,
            "analysis": analysis_result,
            "code_content": code_content,
            "status": "COMPLETED"
        })
        
    except Exception as e:
        import traceback
        print(f"[BACKGROUND ERROR] {traceback.format_exc()}")


    
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
