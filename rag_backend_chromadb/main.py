import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil
from langchain_openai import AzureChatOpenAI
from config import (
    UPLOAD_DIR,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    CHROMA_DB_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    ALLOWED_EXTENSIONS,
)
from document_processor import DocumentProcessor
from vector_store import VectorStore
from fastapi.responses import FileResponse as FastAPIFileResponse

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Create logger
    logger = logging.getLogger(__name__)
    return logger

# Initialize logger
logger = setup_logging()

app = FastAPI(title="RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore()
llm = AzureChatOpenAI(
    azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
    openai_api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    temperature=0
)

# Models
class Question(BaseModel):
    text: str
    user_id: str
    file_id: Optional[str] = None

class FileResponse(BaseModel):
    file_id: str
    filename: str
    chunks: int

class FileContentResponse(BaseModel):
    path: str
    media_type: str
    filename: str

class FileList(BaseModel):
    files: List[dict]

class DeleteFileRequest(BaseModel):
    file_id: str
    user_id: str

# Helper function to get user ID (replace with authentication logic)
async def get_user_id(user_id: str = None):
    if not user_id:
        logger.error("User ID is missing")
        raise HTTPException(status_code=401, detail="User ID is required")
    return user_id

@app.post("/upload/", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """Handle file upload and process it for RAG."""
    try:
        logger.info(f"Processing file upload: {file.filename} for user: {user_id}")
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_DIR):
            logger.info(f"Creating uploads directory at: {UPLOAD_DIR}")
            os.makedirs(UPLOAD_DIR)
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        logger.info(f"Saving uploaded file to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("File saved successfully")

        # Process the document
        logger.info("Processing document into chunks")
        chunks = document_processor.process_document(file_path)
        logger.info(f"Document processed into {len(chunks)} chunks")
        
        # Store in vector database
        logger.info("Storing document in vector database")
        file_id = vector_store.add_documents(
            chunks=chunks,
            user_id=user_id,
            filename=file.filename
        )
        logger.info(f"File stored in vector database with ID: {file_id}")

        # Verify file still exists
        if not os.path.exists(file_path):
            logger.error(f"File was deleted after processing: {file_path}")
            raise HTTPException(status_code=500, detail="File was deleted after processing")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/")
async def ask_question(question: Question):
    """Handle question answering using RAG."""
    try:
        logger.info(f"Processing question for user {question.user_id}: {question.text}")
        
        # Search for relevant chunks
        relevant_chunks = vector_store.search(
            query=question.text,
            user_id=question.user_id,
            file_id=question.file_id
        )
        
        if not relevant_chunks:
            logger.warning(f"No relevant chunks found for question: {question.text}")
            return {"answer": "I couldn't find any relevant information to answer your question."}

        # Prepare context from chunks
        context = "\n\n".join(chunk["text"] for chunk in relevant_chunks)
        logger.info(f"Found {len(relevant_chunks)} relevant chunks")
        
        # Create prompt for the LLM
        prompt = f"""Based on the following context, please answer the question. 
        If the answer cannot be found in the context, say so.

        Context:
        {context}

        Question: {question.text}

        Answer:"""

        # Generate response
        response = llm.invoke(prompt)
        logger.info("Generated response from LLM")
        
        return {
            "answer": response.content,
            "sources": [
                {
                    "filename": chunk["metadata"]["filename"],
                    "chunk_index": chunk["metadata"]["chunk_index"]
                }
                for chunk in relevant_chunks
            ]
        }

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{user_id}", response_model=FileList)
async def list_user_files(user_id: str):
    """List all files uploaded by a user."""
    try:
        logger.info(f"Listing files for user: {user_id}")
        files = vector_store.get_user_files(user_id)
        logger.info(f"Found {len(files)} files for user {user_id}")
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/")
async def delete_file(request: DeleteFileRequest):
    """Delete a file and all its chunks."""
    try:
        logger.info(f"Attempting to delete file {request.file_id} for user {request.user_id}")
        
        # Get file info before deleting from vector store
        file_info = vector_store.get_file_info(request.file_id, request.user_id)
        if not file_info:
            logger.warning(f"File deletion failed: {request.file_id} - File not found in vector store")
            raise HTTPException(status_code=404, detail="File not found or access denied")
            
        # Delete from vector store
        success = vector_store.delete_file(
            file_id=request.file_id,
            user_id=request.user_id
        )
        
        if not success:
            logger.warning(f"File deletion failed: {request.file_id}")
            raise HTTPException(status_code=404, detail="File not found or access denied")
            
        # Delete physical file
        file_path = os.path.join(UPLOAD_DIR, file_info["filename"])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Successfully deleted physical file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting physical file {file_path}: {str(e)}")
                # Don't raise an error here, as the vector store deletion was successful
        else:
            logger.warning(f"Physical file not found at path: {file_path}")
            
        logger.info(f"Successfully deleted file: {request.file_id}")
        return {"message": "File deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{user_id}/{file_id}/content")
async def get_file_content(user_id: str, file_id: str):
    """Serve the content of a file."""
    try:
        logger.info(f"Fetching content for file {file_id} for user {user_id}")
        file_info = vector_store.get_file_info(file_id, user_id)
        logger.info(f"File info from vector store: {file_info}")
        
        if not file_info:
            logger.error(f"No file info found for file_id {file_id} and user_id {user_id}")
            raise HTTPException(status_code=404, detail="File not found or access denied")
            
        file_path = os.path.join(UPLOAD_DIR, file_info["filename"])
        logger.info(f"Looking for file at path: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
            
        # Determine the media type based on file extension
        media_type = "application/octet-stream"
        if file_info["filename"].lower().endswith('.pdf'):
            media_type = "application/pdf"
        elif file_info["filename"].lower().endswith('.txt'):
            media_type = "text/plain"
        elif file_info["filename"].lower().endswith('.doc'):
            media_type = "application/msword"
        elif file_info["filename"].lower().endswith('.docx'):
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
        logger.info(f"Serving file with media type: {media_type}")
        return FastAPIFileResponse(
            path=file_path,
            media_type=media_type,
            filename=file_info["filename"]
        )
    except Exception as e:
        logger.error(f"Error serving file content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    # uvicorn.run("main:app", reload=True)