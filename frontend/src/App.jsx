import React, { useState } from 'react';
import Editor from "@monaco-editor/react";
import { FolderCode, GitBranch, FileCode, Play } from 'lucide-react';
import './App.css';

function App() {
  // TODO : 1. 가상의 파일 데이터 (나중에 백엔드 API로 교체될 부분)
  const files = {
    'Main.java': {
      content: 'public class Main {\n  public static void main(String[] args) {\n    System.out.println("Hello Codin-Nator!");\n  }\n}',
      language: 'java'
    },
    'Preprocessing.py': {
      content: 'import pandas as pd\n\ndef process_data(file_path):\n    print(f"Processing {file_path}...")',
      language: 'python'
    }
  };

  const [selectedFile, setSelectedFile] = useState('Main.java');
  const [code, setCode] = useState(files['Main.java'].content);

  // 파일 클릭 시 변경 핸들러
  const handleFileClick = (fileName) => {
    setSelectedFile(fileName);
    setCode(files[fileName].content);
  };

  return (
    <div className="ide-container">
      {/* 1. 사이드바 */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <FolderCode size={16} style={{display:'inline', marginRight:'5px'}}/> 
          Project Explorer
        </div>
        
        <ul className="file-list">
          {Object.keys(files).map((fileName) => (
            <li 
              key={fileName}
              className={`file-item ${selectedFile === fileName ? 'active' : ''}`}
              onClick={() => handleFileClick(fileName)}
              style={selectedFile === fileName ? {color: '#fff', backgroundColor: '#37373d'} : {}}
            >
              <FileCode 
                size={16} 
                color={fileName.endsWith('.java') ? "#dcb67f" : "#4d9375"} 
              /> 
              {fileName}
            </li>
          ))}
        </ul>

        <div className="git-section">
          <div style={{marginBottom: '10px', fontSize:'0.85rem', fontWeight:'bold'}}>
            <GitBranch size={16} style={{display:'inline', verticalAlign:'middle'}}/> Source Control
          </div>
          <input 
            type="text" 
            placeholder="커밋 메시지 (Message)" 
            className="input-box"
          />
          <button className="btn-primary">
            Commit & Push
          </button>
        </div>
      </aside>

      {/* 2. 메인 에디터 */}
      <main className="editor-area">
        <div className="editor-tabs">
          {/* 현재 선택된 파일에 따라 탭 활성화 표시 */}
          {Object.keys(files).map((fileName) => (
            <div 
              key={fileName} 
              className={`tab ${selectedFile === fileName ? 'active' : ''}`}
              onClick={() => handleFileClick(fileName)}
            >
              {fileName}
            </div>
          ))}
          
          <div className="tabs-right-section">
            <button 
              className="ai-run-btn"
              onClick={() => alert(`${selectedFile} AI 분석 서버 가동!`)}
            >
              <Play size={28} fill="currentColor" /> AI RUN
            </button>
          </div>
        </div>
        
        <div className="editor-wrapper">
          <Editor 
            height="100%" 
            width="100%"
            theme="vs-dark" 
            // 선택된 파일의 확장자에 따라 언어 자동 설정
            language={files[selectedFile].language} 
            value={code} 
            onChange={(val) => setCode(val)} 
            options={{
              automaticLayout: true,
              fontSize: 32,             // 24px도 작다! 32px로 파격 상향 ㅋ
              lineHeight: 48,           // 글자가 커진 만큼 줄 간격도 넉넉하게 (1.5배)
              fontWeight: "600",        // 글자를 좀 더 도톰하게 해서 눈에 확 띄게
              letterSpacing: 1,         // 자간을 살짝 벌려서 가독성 확보
              minimap: { 
                enabled: false 
              },
              cursorWidth: 4,           // 커서 두께도 키워서 어디 있는지 바로 보이게
              scrollBeyondLastLine: false,
              wordWrap: "on",
              padding: { top: 30, bottom: 30 } // 위아래 여백도 넉넉히
            }}
          />
        </div>
      </main>
    </div>
  );
}

export default App;