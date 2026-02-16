# FastAPI, 비동기 통신 학습 프로젝트

본 프로젝트는 **Django**와 **FastAPI** 그리고 **React**의 통신 메커니즘을 학습하기 위한 코드 분석 도구입니다.

## 아키텍처 (Architecture)

- **Frontend**: React (Polling 2s)
- **Backend (Storage)**: Django (SQLite3)
- **AI Engine**: FastAPI (gemini-3-flash-preview)

## 가동 순서 (Execution SOP)

### 1. Backend (Django)

```
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 2. AI Engine (FastAPI)

```
cd ai_server
pip install -r requirements.txt
uvicorn main:app --reload --port 9000
```

### 3. frontend (React)

```
cd frontend
npm install
npm run dev
```

### 통신부문 학습내용 정리

1. 세 기계(React, Django, FastAPI)를 유기적으로 연결하는 법을 학습
   - [기능분리] 특히, 저장 및 사용자 관리(Django)와 고부하 연산(FastAPI)을 분리
   - [UX개선] Django가 FastAPI에 분석을 요청할 때 응답을 기다리지 않고 콜백하여 받음. 이를 프론트엔드에서 2초마다 확인하는 방식을 채택

2. 양방향 통신: 비동기 콜백과 폴링으로 동기화
   - FastAPI → Django (Callback): Django는 기다리지 않음. FastAPI는 연산 완료시 결과를 전송함
   - Frontend → Django (Polling): 앞서 말한 것과 같이 2초 간격으로 DB를 확인.

### 주요기능

_이는 ai 연산을 통해 만들어졌습니다._

```
backend\git_app/views.py
[분석 결과: Git 연동 및 버전 관리 제어기]
- 구조 분석: GitPython 라이브러리를 사용하여 로컬 저장소의 상태(브랜치, 변경 파일)를 조회하고 스테이징, 커밋, 푸시 작업을 수행하는 DRF 기반 컨트롤러입니다. 외부 컨텍스트(`current_context`)에서 경로 정보를 동적으로 참조하여 물리적 저장소를 제어합니다.
- 통신 관점: 저장소의 현재 상태 정보는 `/result` 창구의 폴링 데이터로 활용되며, 커밋 및 푸시와 같은 상태 변경 작업은 처리 완료 후 `/callback` 엔드포인트를 통해 '바구니(DB)'에 성공 여부를 적재하기에 적합한 비동기 후보 로직입니다.
```

```
backend\files/views.py
[분석 결과: 파일 시스템 탐색 및 관리 로직]
- 구조 분석: 전역 변수 `current_context`를 활용하여 서버 메모리 내에 작업 경로를 유지하고, `os.walk`를 통한 재귀적 트리 생성 및 파일 CRUD(조회/수정)를 수행하는 Django Rest Framework 기반의 로직입니다. `.git`, `node_modules` 등 불필요한 경로를 제외하는 필터링 메커니즘이 포함되어 있습니다.
- 통신 관점: 이 코드를 통해 추출된 파일 트리 정보와 파일 본문 데이터는 '사과'로 정의되어 `/api/ai/callback/` 엔드포인트를 통해 비동기적으로 전송될 예정입니다. 최종적으로 Django DB 바구니에 적재된 후, 사용자는 `/api/ai/result/`를 통해 해당 데이터의 상태를 확인할 수 있는 구조입니다.
```

```
backend\ai/views.py
[분석 결과: 비동기 분석 파이프라인 및 콜백 처리기]
- 구조 분석: 요청 중계(FastAPI 연동), 결과 수신(Callback 처리), 상태 조회(Polling)로 구성된 전형적인 비동기 분산 아키텍처입니다. Django ORM(`AnalysisResult`)을 사용하여 전송받은 '사과(데이터)'를 '바구니(DB)'에 안전하게 적재하고 관리하는 구조를 갖추고 있습니다.
- 통신 관점: FastAPI 엔진으로부터 /api/ai/callback/ 경로를 통해 전달된 데이터가 `receive_analysis_callback`에서 처리되어 DB로 인입됩니다. 이후 사용자는 `get_analysis_result` 함수가 매핑된 /api/ai/result/ 엔드포인트를 폴링하여 적재된 최종 결과물을 획득할 수 있습니다.
```
