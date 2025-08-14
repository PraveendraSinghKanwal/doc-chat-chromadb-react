import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import { getFileContent } from '../services/api';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const DocumentViewer = ({ document, userId }) => {
  const [numPages, setNumPages] = useState(null);
  const [documentUrl, setDocumentUrl] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('DocumentViewer: Document prop changed:', document);
    if (document && document.file_id) {
      console.log('DocumentViewer: Fetching document content for:', document.file_id);
      const fetchDocument = async () => {
        try {
          const blob = await getFileContent(userId, document.file_id);
          console.log('DocumentViewer: Received blob:', blob);
          const url = URL.createObjectURL(blob);
          setDocumentUrl(url);
          setError(null);
        } catch (err) {
          console.error('Error fetching document:', err);
          setError(err.message || 'Failed to load document');
        }
      };

      fetchDocument();

      return () => {
        if (documentUrl) {
          URL.revokeObjectURL(documentUrl);
        }
      };
    }
  }, [document, userId]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  if (!document) {
    return (
      <div className="document-viewer empty">
        <p>No document selected</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="document-viewer error">
        <p>{error}</p>
      </div>
    );
  }

  if (!documentUrl) {
    return (
      <div className="document-viewer loading">
        <p>Loading document...</p>
      </div>
    );
  }

  // Check if the file is a PDF based on the filename
  const isPDF = document.filename?.toLowerCase().endsWith('.pdf');

  if (isPDF) {
    return (
      <div className="document-viewer pdf">
        <Document
          file={documentUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div>Loading PDF...</div>}
          error={<div>Error loading PDF. Please try again.</div>}
        >
          {Array.from(new Array(numPages || 0), (_, index) => (
            <Page
              key={`page_${index + 1}`}
              pageNumber={index + 1}
              width={Math.min(800, window.innerWidth - 750)}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          ))}
        </Document>
      </div>
    );
  }

  // For non-PDF files, use an iframe
  return (
    <div className="document-viewer text">
      <iframe
        src={documentUrl}
        title="Document Viewer"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          backgroundColor: 'white'
        }}
      />
    </div>
  );
};

export default DocumentViewer; 