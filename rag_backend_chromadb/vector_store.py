from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import AzureOpenAIEmbeddings
import datetime
import uuid
import logging
from config import (
    CHROMA_DB_DIR,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    TOP_K_RESULTS,
)

# Set up logging
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        try:
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                openai_api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                openai_api_version=AZURE_OPENAI_API_VERSION,
            )
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DB_DIR),
                settings=Settings(allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("VectorStore initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing VectorStore: {str(e)}", exc_info=True)
            raise

    def add_documents(self, chunks: List[str], user_id: str, filename: str, metadata: Optional[Dict] = None):
        """Add document chunks to the vector store with user and file tracking.
        
        Args:
            chunks: List of text chunks
            user_id: Unique identifier for the user
            filename: Original filename
            metadata: Additional metadata to store with chunks
        """
        try:
            if not chunks:
                logger.warning("No chunks provided to add_documents")
                return None

            # Generate a unique file ID
            file_id = str(uuid.uuid4())
            # Convert datetime to ISO format string
            timestamp = datetime.datetime.now().isoformat()

            logger.info(f"Processing {len(chunks)} chunks for file {filename} (ID: {file_id})")

            # Prepare metadata for each chunk
            chunk_metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "user_id": str(user_id),  # Ensure user_id is string
                    "file_id": file_id,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "timestamp": timestamp,
                }
                if metadata:
                    chunk_metadata.update(metadata)
                chunk_metadatas.append(chunk_metadata)

            # Generate embeddings for chunks
            logger.info("Generating embeddings for chunks")
            embeddings = self.embeddings.embed_documents(chunks)
            
            # Add to ChromaDB with detailed metadata
            logger.info("Adding documents to ChromaDB")
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=[f"{file_id}_chunk_{i}" for i in range(len(chunks))]
            )
            logger.info(f"Successfully added documents to ChromaDB with file_id: {file_id}")
            return file_id

        except Exception as e:
            logger.error(f"Error in add_documents: {str(e)}", exc_info=True)
            raise

    def search(self, query: str, user_id: Optional[str] = None, file_id: Optional[str] = None) -> List[Dict]:
        """Search for similar chunks in the vector store with optional filtering.
        
        Args:
            query: The search query
            user_id: Optional user ID to filter results
            file_id: Optional file ID to filter results
            
        Returns:
            List of dictionaries containing chunks and their metadata
        """
        try:
            logger.info(f"Searching for query: {query}")
            if user_id:
                logger.info(f"Filtering by user_id: {user_id}")
            if file_id:
                logger.info(f"Filtering by file_id: {file_id}")

            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Prepare where clause for filtering
            where = None
            if user_id and file_id:
                where = {
                    "$and": [
                        {"user_id": {"$eq": str(user_id)}},  # Ensure user_id is string
                        {"file_id": {"$eq": file_id}}
                    ]
                }
            elif user_id:
                where = {"user_id": {"$eq": str(user_id)}}  # Ensure user_id is string
            elif file_id:
                where = {"file_id": {"$eq": file_id}}
            
            # Search in ChromaDB
            logger.info("Executing search in ChromaDB")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=TOP_K_RESULTS,
                where=where
            )
            
            # Combine documents with their metadata
            if results["documents"] and results["metadatas"]:
                logger.info(f"Found {len(results['documents'][0])} relevant chunks")
                return [
                    {
                        "text": doc,
                        "metadata": meta
                    }
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0])
                ]
            logger.info("No relevant chunks found")
            return []

        except Exception as e:
            logger.error(f"Error in search: {str(e)}", exc_info=True)
            raise

    def get_user_files(self, user_id: str) -> List[Dict]:
        """Get all files uploaded by a specific user.
        
        Args:
            user_id: The user ID to search for
            
        Returns:
            List of unique files with their metadata
        """
        try:
            logger.info(f"Getting files for user_id: {user_id}")
            # Get all documents for the user
            results = self.collection.get(
                where={"user_id": {"$eq": str(user_id)}}  # Ensure user_id is string
            )
            
            if not results["metadatas"]:
                logger.info(f"No files found for user_id: {user_id}")
                return []
                
            # Group by file_id and get unique files
            files = {}
            for metadata in results["metadatas"]:
                file_id = metadata["file_id"]
                if file_id not in files:
                    files[file_id] = {
                        "file_id": file_id,
                        "filename": metadata["filename"],
                        "upload_time": metadata["timestamp"],
                        "total_chunks": metadata["total_chunks"]
                    }
            
            logger.info(f"Found {len(files)} unique files for user_id: {user_id}")
            return list(files.values())

        except Exception as e:
            logger.error(f"Error in get_user_files: {str(e)}", exc_info=True)
            raise

    def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete all chunks associated with a specific file.
        
        Args:
            file_id: The file ID to delete
            user_id: The user ID who owns the file
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            logger.info(f"Deleting file {file_id} for user {user_id}")
            # Delete all chunks for this file
            self.collection.delete(
                where={
                    "$and": [
                        {"file_id": {"$eq": file_id}},
                        {"user_id": {"$eq": str(user_id)}}  # Ensure user_id is string
                    ]
                }
            )
            logger.info(f"Successfully deleted file {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error in delete_file: {str(e)}", exc_info=True)
            raise

    def get_file_info(self, file_id: str, user_id: str) -> Optional[Dict]:
        """Get information about a specific file.
        
        Args:
            file_id: The file ID to look up
            user_id: The user ID who owns the file
            
        Returns:
            Dict containing file information or None if not found
        """
        try:
            logger.info(f"Getting info for file {file_id} for user {user_id}")
            # Get the first chunk's metadata for this file
            results = self.collection.get(
                where={
                    "$and": [
                        {"file_id": {"$eq": file_id}},
                        {"user_id": {"$eq": str(user_id)}}  # Ensure user_id is string
                    ]
                },
                limit=1
            )
            
            if not results["metadatas"]:
                logger.info(f"No file found with ID {file_id} for user {user_id}")
                return None
                
            metadata = results["metadatas"][0]
            return {
                "file_id": metadata["file_id"],
                "filename": metadata["filename"],
                "upload_time": metadata["timestamp"],
                "total_chunks": metadata["total_chunks"]
            }
            
        except Exception as e:
            logger.error(f"Error in get_file_info: {str(e)}", exc_info=True)
            raise 