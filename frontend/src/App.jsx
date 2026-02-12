import React, { useState, useEffect, useRef } from 'react';
import Editor from "@monaco-editor/react";
import { FolderCode, GitBranch, FileCode, Play, FolderOpen, Bot, X } from 'lucide-react';
import axios from 'axios';
import './App.css';

function App() {
  const [rootPath, setRootPath] = useState('');
  const [fileList, setFileList] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [code, setCode] = useState('// 프로젝트를 불러오면 코드가 여기에 표시됩니다.');
  const [language, setLanguage] = useState('javascript');
  const [commitMessage, setCommitMessage] = useState('');

  // --- [공정 1] AI 상태 관리 변수 정비 ---
  const [aiResponse, setAiResponse] = useState('');     // 화면에 한 글자씩 표시될 텍스트
  const [fullAnalysis, setFullAnalysis] = useState(''); // 서버에서 받은 전체 원본 텍스트
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [isTyping, setIsTyping] = useState(false);      // 타이핑 효과 진행 중 여부

  const loadProject = async () => {

    try {

      const response = await axios.post('http://127.0.0.1:8000/api/files/list/', { root_path: rootPath });

      const safeFileList = response.data.filter(file => file.name !== '.env');

      setFileList(safeFileList);

    } catch (error) {

      console.error("로딩 실패:", error);

      alert("경로가 올바르지 않거나 서버 연결에 실패했습니다.");

    }

  };



  const handleFileClick = async (dirPath, fileName) => {

    const relativePath = dirPath === "root" ? fileName : `${dirPath}/${fileName}`;

    try {

      const response = await axios.post('http://127.0.0.1:8000/api/files/detail/', { path: relativePath });

      setSelectedFile(relativePath);

      setCode(response.data.content);

      if (fileName.endsWith('.java')) setLanguage('java');

      else if (fileName.endsWith('.py')) setLanguage('python');

      else if (fileName.endsWith('.js') || fileName.endsWith('.jsx')) setLanguage('javascript');

      else setLanguage('plaintext');

    } catch (error) {

      alert("파일 내용을 읽어오지 못했습니다.");

    }

  };


  // --- [공정 2] AI RUN 로직: 비동기 폴링 이식 ---
  const handleAIRun = async () => {
    if (!selectedFile) return alert("분석할 파일을 선택해주세요.");

    setIsAnalyzing(true);
    setShowAiPanel(true);
    setAiResponse("AI 분석가가 코드를 정밀 검토 중입니다..."); // 초기 대기 메시지
    setFullAnalysis("");

    try {
      // 1. 분석 요청 트리거 (Django -> FastAPI)
      await axios.post('http://127.0.0.1:8000/api/ai/results/', {
        filename: selectedFile,
        code_content: code
      });

      // 2. 결과가 DB에 저장될 때까지 추적 (Polling)
      startPolling(selectedFile);
    } catch (error) {
      setAiResponse("분석 요청 중 오류가 발생했습니다.");
      setIsAnalyzing(false);
    }
  };
// useRef를 사용하여 인터벌 ID를 안전하게 관리
const pollingRef = useRef(null);

const startPolling = (filename) => {
  // [보정] 기존에 가동 중인 선로가 있다면 폐쇄
  if (pollingRef.current) clearInterval(pollingRef.current);

  pollingRef.current = setInterval(async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/ai/summaries/?filename=${filename}`);
      
      if (response.data.analysis) {
        setFullAnalysis(response.data.analysis);
        setIsTyping(true);
      }

      // [세션 확정] 'COMPLETED' 신호를 받으면 즉시 선로 폐쇄
      if (response.data.status === 'COMPLETED') {
        clearInterval(pollingRef.current);
        setIsAnalyzing(false);
        setFullAnalysis(response.data.analysis); // 최종 데이터 확정
        console.log(`[SESSION FIXED] ID: ${response.data.id} 확정.`);
      }
    } catch (err) {
      // 404나 200 processing 상태는 무시하고 계속 폴링
    }
  }, 2000);
};

// --- 타이핑 효과 엔진 (정밀 보정형) ---
useEffect(() => {
  if (isTyping && fullAnalysis) {
    const timer = setInterval(() => {
      // functional update를 사용하여 최신 상태 기반으로 인덱스 계산
      setAiResponse((currentVisible) => {
        const nextIndex = currentVisible.length;
        if (nextIndex < fullAnalysis.length) {
          return currentVisible + fullAnalysis.charAt(nextIndex);
        } else {
          // 타이핑이 데이터 끝에 도달했을 때
          if (!isAnalyzing) {
            clearInterval(timer);
            setIsTyping(false);
          }
          return currentVisible;
        }
      });
    }, 20);
    return () => clearInterval(timer);
  }
}, [fullAnalysis, isTyping, isAnalyzing]); // aiResponse는 내부 업데이트로 처리하므로 제외 가능



  const handleGitAction = async () => {
    if (!commitMessage.trim()) return alert("커밋 메시지를 입력해주세요.");
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/git_app/commit/', { message: commitMessage });
      alert(response.data.message);
      setCommitMessage('');
    } catch (error) {
      alert("Git 오류 발생");
    }
  };

  return (
    <div className="ide-container">
      <aside className="sidebar">
        <div className="sidebar-header"><FolderOpen size={16} style={{ marginRight: '5px' }} /> Path Setup</div>
        <div className="path-input-section" style={{ padding: '10px' }}>
          <input type="text" className="input-box" placeholder="Absolute Path" value={rootPath} onChange={(e) => setRootPath(e.target.value)} />
          <button className="btn-primary" onClick={loadProject}>Load Project</button>
        </div>
        <div className="sidebar-header" style={{ borderTop: '1px solid #3c3c3c', marginTop: '10px' }}><FolderCode size={16} style={{ marginRight: '5px' }} /> Project Explorer</div>
        <ul className="file-list">
          {fileList.map((dir, idx) => (
            <div key={idx}>
              <li className="dir-item" style={{ fontSize: '0.75rem', color: '#858585', padding: '5px 10px' }}>{dir.directory}</li>
              {dir.files.map((file) => {
                const path = dir.directory === "root" ? file : `${dir.directory}/${file}`;
                return (
                  <li key={path} className={`file-item ${selectedFile === path ? 'active' : ''}`} onClick={() => handleFileClick(dir.directory, file)}>
                    <FileCode size={16} color={file.endsWith('.java') ? "#dcb67f" : "#4d9375"} /> {file}
                  </li>
                );
              })}
            </div>
          ))}
        </ul>
        <div className="git-section">
          <div style={{ marginBottom: '10px', fontSize: '0.85rem', fontWeight: 'bold' }}><GitBranch size={16} style={{ display: 'inline', verticalAlign: 'middle' }} /> Source Control</div>
          <input type="text" placeholder="Message" className="input-box" value={commitMessage} onChange={(e) => setCommitMessage(e.target.value)} />
          <button className="btn-primary" onClick={handleGitAction}>Commit & Push</button>
        </div>
      </aside>

      <main className={`editor-area ${showAiPanel ? 'panel-open' : ''}`}>
        <div className="editor-tabs">
          {selectedFile && <div className="tab active">{selectedFile.split('/').pop()}</div>}
          <div className="tabs-right-section">
            <button className={`ai-run-btn ${isAnalyzing ? 'loading' : ''}`} onClick={handleAIRun} disabled={isAnalyzing || isTyping}>
              <Play size={28} fill="currentColor" /> {isAnalyzing ? 'ANALYZING...' : (isTyping ? 'TYPING...' : 'AI RUN')}
            </button>
          </div>
        </div>
        <div className="editor-wrapper">
          <Editor height="100%" theme="vs-dark" language={language} value={code} onChange={(val) => setCode(val)} options={{ automaticLayout: true, fontSize: 32, fontWeight: "600", minimap: { enabled: false }, wordWrap: "on" }} />
        </div>
      </main>

      {showAiPanel && (
        <aside className="ai-panel">
          <div className="panel-header">
            <div className="header-title"><Bot size={18} style={{ marginRight: '8px' }} /> AI Analysis</div>
            <button className="close-btn" onClick={() => setShowAiPanel(false)}><X size={18} /></button>
          </div>
          <div className="panel-content">
            {/* 타이핑 효과를 위해 pre 태그 유지, 커서 효과 애니메이션 추가 권장 */}
            <pre className="ai-text">
              {aiResponse}
              {isTyping && <span className="cursor">|</span>}
            </pre>
          </div>
        </aside>
      )}
    </div>
  );
}

export default App;