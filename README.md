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
