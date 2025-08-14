from typing import List
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from config import CHUNK_SIZE, CHUNK_OVERLAP, ALLOWED_EXTENSIONS
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )

    def get_loader(self, file_path: str):
        """Get the appropriate loader based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()[1:]
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        if ext == "pdf":
            return PyPDFLoader(file_path)
        elif ext == "txt":
            return TextLoader(file_path)
        elif ext in ["doc", "docx"]:
            return UnstructuredWordDocumentLoader(file_path)
        else:
            raise ValueError(f"No loader available for {ext}")

    def process_document(self, file_path: str) -> List[str]:
        """Process a document and return chunks of text."""
        try:
            logger.info(f"Processing document at path: {file_path}")
            if not os.path.exists(file_path):
                logger.error(f"File not found at path: {file_path}")
                raise Exception(f"File not found: {file_path}")
                
            loader = self.get_loader(file_path)
            logger.info("Loading document with loader")
            documents = loader.load()
            logger.info(f"Document loaded, splitting into chunks")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Document split into {len(chunks)} chunks")
            
            # Verify file still exists after processing
            if not os.path.exists(file_path):
                logger.error(f"File was deleted during processing: {file_path}")
                raise Exception(f"File was deleted during processing: {file_path}")
                
            return [chunk.page_content for chunk in chunks]
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise Exception(f"Error processing document: {str(e)}") 