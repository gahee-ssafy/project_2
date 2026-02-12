import React, { useState } from 'react';
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

  // --- [기계적 수리] 누락된 상태값 추가 ---
  const [aiResponse, setAiResponse] = useState(''); 
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);

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

  // --- [기계적 수리] 누락된 AI RUN 함수 추가 ---
  const handleAIRun = async () => {
    if (!selectedFile) return alert("분석할 파일을 선택해주세요.");
    setIsAnalyzing(true);
    setShowAiPanel(true);
    setAiResponse("AI 분석가가 코드를 검토 중입니다...");
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/ai/results/', {
        filename: selectedFile,
        code_content: code
      });
      setAiResponse(response.data.analysis || "분석 결과를 가져오지 못했습니다.");
    } catch (error) {
      setAiResponse("분석 중 에러가 발생했습니다.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="ide-container">
      <aside className="sidebar">
        <div className="sidebar-header"><FolderOpen size={16} style={{marginRight:'5px'}}/> Path Setup</div>
        <div className="path-input-section" style={{padding: '10px'}}>
          <input type="text" className="input-box" placeholder="Absolute Path" value={rootPath} onChange={(e) => setRootPath(e.target.value)} />
          <button className="btn-primary" onClick={loadProject}>Load Project</button>
        </div>
        <div className="sidebar-header" style={{borderTop: '1px solid #3c3c3c', marginTop: '10px'}}><FolderCode size={16} style={{marginRight:'5px'}}/> Project Explorer</div>
        <ul className="file-list">
          {fileList.map((dir, idx) => (
            <div key={idx}>
              <li className="dir-item" style={{fontSize: '0.75rem', color: '#858585', padding: '5px 10px'}}>{dir.directory}</li>
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
          <div style={{marginBottom: '10px', fontSize:'0.85rem', fontWeight:'bold'}}><GitBranch size={16} style={{display:'inline', verticalAlign:'middle'}}/> Source Control</div>
          <input type="text" placeholder="Message" className="input-box" value={commitMessage} onChange={(e) => setCommitMessage(e.target.value)} />
          <button className="btn-primary" onClick={handleGitAction}>Commit & Push</button>
        </div>
      </aside>

      <main className={`editor-area ${showAiPanel ? 'panel-open' : ''}`}>
        <div className="editor-tabs">
          {selectedFile && <div className="tab active">{selectedFile.split('/').pop()}</div>}
          <div className="tabs-right-section">
            <button className={`ai-run-btn ${isAnalyzing ? 'loading' : ''}`} onClick={handleAIRun} disabled={isAnalyzing}>
              <Play size={28} fill="currentColor" /> {isAnalyzing ? 'ANALYZING...' : 'AI RUN'}
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
            <div className="header-title"><Bot size={18} style={{marginRight: '8px'}}/> AI Analysis</div>
            <button className="close-btn" onClick={() => setShowAiPanel(false)}><X size={18} /></button>
          </div>
          <div className="panel-content"><pre className="ai-text">{aiResponse}</pre></div>
        </aside>
      )}
    </div>
  );
}

export default App;