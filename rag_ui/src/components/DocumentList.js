import React, { useRef, useState, useEffect } from 'react';
import { uploadDocument, deleteDocument, listUserFiles } from '../services/api';

const DocumentList = ({
  selectedDocument,
  onDocumentSelect,
  onDocumentUpload,
  userId
}) => {
  const fileInputRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetchUserFiles();
  }, [userId]);

  const fetchUserFiles = async () => {
    try {
      const response = await listUserFiles(userId);
      setDocuments(response.files);
    } catch (error) {
      console.error('Error fetching files:', error);
      setError('Failed to fetch documents. Please try again.');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (file) {
      setIsLoading(true);
      setUploadProgress(0);
      setError(null);

      try {
        const uploadResponse = await uploadDocument(file, userId);
        console.log('Upload response:', uploadResponse);
        
        // Update the documents list with the new file
        const newFile = {
          file_id: uploadResponse.file_id,
          filename: uploadResponse.filename,
          chunks: uploadResponse.chunks,
          upload_time: new Date().toISOString()
        };
        
        console.log('New file object:', newFile);
        setDocuments(prevDocs => [...prevDocs, newFile]);
        onDocumentUpload(newFile);
        setUploadProgress(100);
      } catch (error) {
        console.error('Error processing file:', error);
        setError('Failed to upload document. Please try again.');
      } finally {
        setIsLoading(false);
        event.target.value = '';
      }
    }
  };

  const handleDeleteDocument = async (event, doc) => {
    event.stopPropagation();
    try {
      await deleteDocument(doc.file_id, userId);
      
      // Update UI
      setDocuments(prevDocs => prevDocs.filter(d => d.file_id !== doc.file_id));
      if (selectedDocument && selectedDocument.file_id === doc.file_id) {
        onDocumentSelect(null);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      setError('Failed to delete document. Please try again.');
    }
  };

  return (
    <div className="document-list-container">
      <div className="document-list-header">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.txt,.doc,.docx"
          style={{ display: 'none' }}
        />
        <button 
          className="upload-button" 
          onClick={handleUploadClick}
          disabled={isLoading}
        >
          {isLoading ? 'Uploading...' : 'Upload Document'}
        </button>
        
        {isLoading && (
          <div className="upload-progress">
            <div 
              className="progress-bar"
              style={{ width: `${uploadProgress}%` }}
            />
            <span>{uploadProgress}%</span>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      <div className="document-list-scrollable">
        {documents.map((doc) => (
          <div
            key={doc.file_id}
            className={`document-item ${selectedDocument?.file_id === doc.file_id ? 'selected' : ''}`}
            onClick={() => {
              console.log('Document clicked:', doc);
              onDocumentSelect(doc);
            }}
          >
            <div className="document-info">
              <div className="document-name">{doc.filename}</div>
              <div className="document-size">
                Uploaded: {new Date(doc.upload_time).toLocaleDateString()}
              </div>
            </div>
            <button
              className="delete-button"
              onClick={(e) => handleDeleteDocument(e, doc)}
              title="Delete document"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DocumentList; 