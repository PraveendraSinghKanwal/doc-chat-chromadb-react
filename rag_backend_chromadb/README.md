# RAG (Retrieval-Augmented Generation) Backend

A FastAPI-based backend for a Retrieval-Augmented Generation application using Azure OpenAI. This application allows users to upload documents, process them into chunks, store them in a vector database, and ask questions based on the content.

## Features

- **Document Processing**
  - Support for multiple file formats (PDF, TXT, DOC, DOCX)
  - Automatic text extraction and chunking
  - Configurable chunk size and overlap

- **Vector Storage**
  - ChromaDB integration for efficient vector storage
  - Azure OpenAI embeddings for text vectorization
  - Metadata tracking for user and file management

- **Question Answering**
  - Azure OpenAI GPT integration for intelligent responses
  - Context-aware answers based on relevant document chunks
  - Source tracking for answer verification

- **User Management**
  - User-specific document storage and retrieval
  - File management capabilities (list/delete)
  - Secure access control

## Technical Stack

- **Backend Framework**: FastAPI
- **Vector Database**: ChromaDB
- **LLM & Embeddings**: Azure OpenAI
- **Document Processing**: LangChain
- **File Handling**: Python-multipart, Unstructured

## Prerequisites

- Python 3.8+
- Azure OpenAI account with:
  - Embedding model deployment
  - Chat model deployment (GPT-3.5 or GPT-4)
- Azure OpenAI API key and endpoint

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag_backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment-name
AZURE_OPENAI_CHAT_DEPLOYMENT=your-chat-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## Project Structure

```
.
├── main.py              # FastAPI application and endpoints
├── config.py           # Configuration and environment variables
├── document_processor.py # Document processing utilities
├── vector_store.py     # Vector storage and embeddings
├── requirements.txt    # Project dependencies
├── uploads/           # Temporary file storage
├── chroma_db/         # Vector database storage
└── logs/             # Application logs
```

## API Endpoints

### 1. Upload Document
```http
POST /upload/
Content-Type: multipart/form-data
Parameters:
- file: Document file (PDF, TXT, DOC, DOCX)
- user_id: User identifier
Response:
{
    "file_id": "uuid",
    "filename": "original_filename",
    "chunks": number_of_chunks
}
```

### 2. Ask Question
```http
POST /ask/
Content-Type: application/json
Request Body:
{
    "text": "your question",
    "user_id": "user_id",
    "file_id": "optional_file_id"
}
Response:
{
    "answer": "generated answer",
    "sources": [
        {
            "filename": "source_file",
            "chunk_index": chunk_number
        }
    ]
}
```

### 3. List User Files
```http
GET /files/{user_id}
Response:
{
    "files": [
        {
            "file_id": "uuid",
            "filename": "original_filename",
            "upload_time": "timestamp",
            "total_chunks": number_of_chunks
        }
    ]
}
```

### 4. Delete File
```http
DELETE /files/
Content-Type: application/json
Request Body:
{
    "file_id": "file_uuid",
    "user_id": "user_id"
}
Response:
{
    "message": "File deleted successfully"
}
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Logging

The application includes comprehensive logging:
- Console output for real-time monitoring
- Rotating file logs in the `logs` directory
- Log levels: INFO, WARNING, ERROR
- Detailed error tracking with stack traces

## Error Handling

The application includes robust error handling for:
- File processing errors
- API request validation
- Vector database operations
- Azure OpenAI API interactions

## Security Considerations

- User authentication required for all operations
- File type validation
- Secure file handling
- Temporary file cleanup
- CORS configuration for frontend integration

## Performance Considerations

- Configurable chunk size for optimal processing
- Efficient vector storage with ChromaDB
- Asynchronous API endpoints
- Automatic cleanup of temporary files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, please [contact details or issue tracker information] 