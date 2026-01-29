1. 의존성 설치 (가장 먼저!)

- npm install

2. 가짜 데이터를 '상태(State)'로 전환
   현재 App.jsx에 하드코딩된 files 객체를 서버에서 받아올 수 있도록 useState와 useEffect를 준비해야 합니다.

const [files, setFiles] = useState({}); 처럼 빈 상태를 먼저 만듭니다.

3. Axios 통신 함수 작성
   사진으로 보여주신 API 명세서의 주소들(/files/list, /files/detail)로 요청을 보내는 함수를 만듭니다.

이 함수들이 실행되면 우리가 정한 그 큼직큼직한 사이드바와 에디터에 실제 데이터가 꽂히게 됩니다.
