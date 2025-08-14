import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import DocumentList from './components/DocumentList';
import DocumentViewer from './components/DocumentViewer';
import ChatPanel from './components/ChatPanel';

function App() {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [userId] = useState('user123'); // In a real app, this would come from authentication

  const handleDocumentSelect = (document) => {
    console.log('App: Document selected:', document);
    setSelectedDocument(document);
  };

  const handleDocumentUpload = (document) => {
    console.log('App: Document uploaded:', document);
    setSelectedDocument(document);
  };

  return (
    <div className="app-container">
      <Header />
      <div className="main-content">
        <div className="document-list-panel">
          <DocumentList
            selectedDocument={selectedDocument}
            onDocumentSelect={handleDocumentSelect}
            onDocumentUpload={handleDocumentUpload}
            userId={userId}
          />
        </div>
        <div className="document-viewer-panel">
          <DocumentViewer document={selectedDocument} userId={userId} />
        </div>
        <div className="chat-panel">
          <ChatPanel
            selectedDocument={selectedDocument}
            userId={userId}
          />
        </div>
      </div>
    </div>
  );
}

export default App; 