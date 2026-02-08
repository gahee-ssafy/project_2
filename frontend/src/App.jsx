import React, { useState, useEffect } from 'react';
import Editor from "@monaco-editor/react";
import { FolderCode, GitBranch, FileCode, Play, FolderOpen } from 'lucide-react';
import axios from 'axios';
import './App.css';

function App() {
  const [rootPath, setRootPath] = useState(''); // 프로젝트 절대 경로 상태
  const [fileList, setFileList] = useState([]);  // 백엔드에서 받은 파일 트리
  const [selectedFile, setSelectedFile] = useState(null); // 선택된 파일의 상대 경로
  const [code, setCode] = useState('// 프로젝트를 불러오면 코드가 여기에 표시됩니다.');
  const [language, setLanguage] = useState('javascript');
  const [commitMessage, setCommitMessage] = useState('');


  // 1. 프로젝트 불러오기 (백엔드에 root_path 전송)
  const loadProject = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/files/list/', {
        root_path: rootPath
      });
      setFileList(response.data);
    } catch (error) {
      console.error("로딩 실패:", error);
      alert("경로가 올바르지 않거나 서버 연결에 실패했습니다.");
    }
  };

  // 2. 파일 클릭 시 내용 가져오기
  const handleFileClick = async (dirPath, fileName) => {
    // 상대 경로 생성 (예: "src/main.py")
    const relativePath = dirPath === "root" ? fileName : `${dirPath}/${fileName}`;
    
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/files/detail/', {
        path: relativePath
      });
      
      setSelectedFile(relativePath);
      setCode(response.data.content);
      
      // 확장자에 따른 언어 설정
      if (fileName.endsWith('.java')) setLanguage('java');
      else if (fileName.endsWith('.py')) setLanguage('python');
      else if (fileName.endsWith('.js') || fileName.endsWith('.jsx')) setLanguage('javascript');
      else setLanguage('plaintext');

    } catch (error) {
      alert("파일 내용을 읽어오지 못했습니다.");
    }
  };
  // 3. git 기능 
  const handleGitAction = async () => {
  if (!commitMessage.trim()) {
    alert("커밋 메시지를 입력해주세요.");
    return;
  }
  
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/git_app/commit/', {
      message: commitMessage
    });
    alert(response.data.message);
    setCommitMessage(''); // 성공 시 입력창 초기화
  } catch (error) {
    console.error("Git 오류:", error);
    alert("Git 작업 중 오류 발생: " + (error.response?.data?.error || "서버 연결 확인 필요"));
  }
};
  return (
    <div className="ide-container">
      {/* 1. 사이드바 */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <FolderOpen size={16} style={{marginRight:'5px'}}/>
          Path Setup
        </div>
        
        {/* 경로 입력 섹션 */}
        <div className="path-input-section" style={{padding: '10px'}}>
          <input 
            type="text" 
            className="input-box" 
            placeholder="Absolute Path (C:\...)" 
            value={rootPath}
            onChange={(e) => setRootPath(e.target.value)}
          />
          <button className="btn-primary" onClick={loadProject} style={{marginTop: '5px', width: '100%'}}>
            Load Project
          </button>
        </div>

        <div className="sidebar-header" style={{borderTop: '1px solid #3c3c3c', marginTop: '10px'}}>
          <FolderCode size={16} style={{marginRight:'5px'}}/> 
          Project Explorer
        </div>
        
        <ul className="file-list">
          {fileList.map((dir, idx) => (
            <div key={idx}>
              {/* 디렉토리 이름 표시 (선택 사항) */}
              <li className="dir-item" style={{fontSize: '0.75rem', color: '#858585', padding: '5px 10px'}}>
                {dir.directory}
              </li>
              {dir.files.map((file) => {
                const fullRelativePath = dir.directory === "root" ? file : `${dir.directory}/${file}`;
                return (
                  <li 
                    key={fullRelativePath}
                    className={`file-item ${selectedFile === fullRelativePath ? 'active' : ''}`}
                    onClick={() => handleFileClick(dir.directory, file)}
                  >
                    <FileCode 
                      size={16} 
                      color={file.endsWith('.java') ? "#dcb67f" : "#4d9375"} 
                    /> 
                    {file}
                  </li>
                );
              })}
            </div>
          ))}
        </ul>

        <div className="git-section">
  <div style={{marginBottom: '10px', fontSize:'0.85rem', fontWeight:'bold'}}>
    <GitBranch size={16} style={{display:'inline', verticalAlign:'middle'}}/> Source Control
  </div>
  
  {/* 1. value와 onChange 연결 */}
  <input 
    type="text" 
    placeholder="Message" 
    className="input-box" 
    value={commitMessage}
    onChange={(e) => setCommitMessage(e.target.value)}
  />
  
  {/* 2. onClick 핸들러 연결 */}
  <button className="btn-primary" onClick={handleGitAction}>
    Commit & Push
  </button>
</div>
      </aside>

      {/* 2. 메인 에디터 */}
      <main className="editor-area">
        <div className="editor-tabs">
          {selectedFile && (
            <div className="tab active">
              {selectedFile.split('/').pop()}
            </div>
          )}
          
          <div className="tabs-right-section">
            <button className="ai-run-btn" onClick={() => alert(`${selectedFile} AI 분석 서버 가동!`)}>
              <Play size={28} fill="currentColor" /> AI RUN
            </button>
          </div>
        </div>
        
        <div className="editor-wrapper">
          <Editor 
            height="100%" 
            theme="vs-dark" 
            language={language} 
            value={code} 
            onChange={(val) => setCode(val)} 
            options={{
              automaticLayout: true,
              fontSize: 32,
              fontWeight: "600",
              minimap: { enabled: false },
              wordWrap: "on",
            }}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
