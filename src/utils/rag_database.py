"""
RAG Database - Vector Store for Regulatory Document Validation

This module implements a genuine retrieval-augmented generation (RAG) system
using ChromaDB for document storage and retrieval. This enhances the existing
hardcoded reference sources with dynamic document retrieval.

HYBRID APPROACH:
- RAG database provides dynamic, query-specific context
- Hardcoded baseline sources always included as fallback
- System works even if RAG database is empty

CAPABILITY:
- Add regulatory documents to vector store
- Retrieve relevant passages for risk assessment context
- Validate claims against stored documents
- Support for adding custom regulatory corpus

Created: 2025-01-XX
"""

import os
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    embedding_functions = None


class RAGDatabase:
    """
    Vector database for regulatory document retrieval.
    
    USAGE:
    1. Initialize database (creates persistent store)
    2. Add documents via add_document() or add_documents_from_directory()
    3. Query for relevant context via query() or get_context_for_assessment()
    4. Validate claims via validate_claim()
    
    EXTENSIBILITY:
    Users can add their own regulatory documents to expand the knowledge base.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize RAG database with persistent storage.
        
        Args:
            persist_directory: Directory for ChromaDB persistence
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB not installed. Run: pip install chromadb sentence-transformers"
            )
        
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use sentence-transformers for embeddings (lightweight, local)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="regulatory_documents",
            embedding_function=self.embedding_fn,
            metadata={"description": "IoT regulatory documents and standards for risk assessment"}
        )
        
        print(f"📚 RAG Database initialized: {self.collection.count()} documents")
    
    def add_document(
        self,
        content: str,
        doc_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a single document to the database.
        
        Args:
            content: Document text content
            doc_id: Unique identifier for the document
            metadata: Optional metadata (source, type, year, etc.)
        """
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata or {"added_at": datetime.now().isoformat()}]
        )
    
    def add_documents_from_directory(self, directory: str, file_extensions: List[str] = [".txt", ".md"]) -> int:
        """
        Bulk load documents from a directory.
        
        Args:
            directory: Path to directory containing documents
            file_extensions: List of file extensions to include
            
        Returns:
            Number of documents added
        """
        doc_dir = Path(directory)
        if not doc_dir.exists():
            print(f"⚠️  Directory not found: {directory}")
            return 0
        
        count = 0
        
        for ext in file_extensions:
            for file_path in doc_dir.glob(f"**/*{ext}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    doc_id = f"{file_path.stem}_{hash(file_path)}"
                    metadata = {
                        "source": str(file_path),
                        "filename": file_path.name,
                        "added_at": datetime.now().isoformat()
                    }
                    
                    self.add_document(content, doc_id, metadata)
                    count += 1
                    print(f"  Added: {file_path.name}")
                    
                except Exception as e:
                    print(f"  ⚠️  Failed to add {file_path}: {e}")
        
        return count
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query the database for relevant documents.
        
        Args:
            query_text: The search query
            n_results: Maximum number of results
            where: Optional filter conditions
            
        Returns:
            List of results with content, metadata, and relevance score
        """
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count()),
            where=where
        )
        
        formatted = []
        for i in range(len(results["documents"][0])):
            formatted.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
                "id": results["ids"][0][i]
            })
        
        return formatted
    
    def validate_claim(
        self,
        claim: str,
        threshold: float = 0.5
    ) -> Dict:
        """
        Validate a claim against the document store.
        
        Args:
            claim: The claim to validate
            threshold: Distance threshold (lower = stricter matching)
            
        Returns:
            Validation result with confidence and supporting documents
        """
        results = self.query(claim, n_results=3)
        
        if not results:
            return {
                "validated": False,
                "confidence": 0.0,
                "message": "No relevant documents in database",
                "supporting_docs": []
            }
        
        best_match = results[0]
        distance = best_match.get("distance", 1.0)
        confidence = max(0, 1 - distance)
        validated = distance < threshold
        
        return {
            "validated": validated,
            "confidence": confidence,
            "message": f"{'Supported' if validated else 'Not supported'} by document store (confidence: {confidence:.2%})",
            "supporting_docs": results
        }
    
    def get_context_for_assessment(self, risk_topic: str, n_docs: int = 5) -> str:
        """
        Retrieve relevant context for a risk assessment.
        
        Args:
            risk_topic: The risk topic being assessed
            n_docs: Number of documents to retrieve
            
        Returns:
            Formatted context string for prompt injection
        """
        results = self.query(risk_topic, n_results=n_docs)
        
        if not results:
            return "=== NO REGULATORY CONTEXT AVAILABLE ===\nRAG database is empty or no relevant documents found."
        
        context_parts = [
            "=== RELEVANT REGULATORY CONTEXT (Retrieved via RAG) ===\n",
            f"Query: {risk_topic}\n",
            f"Documents retrieved: {len(results)}\n"
        ]
        
        for i, doc in enumerate(results, 1):
            source = doc["metadata"].get("source", "Unknown")
            confidence = 1 - doc.get("distance", 0) if doc.get("distance") else "N/A"
            context_parts.append(f"\n[Source {i}: {source}]")
            context_parts.append(f"[Relevance: {confidence:.2%}]" if isinstance(confidence, float) else f"[Relevance: {confidence}]")
            # Truncate long documents
            content = doc["content"][:1000] + "..." if len(doc["content"]) > 1000 else doc["content"]
            context_parts.append(f"\n{content}\n")
        
        return "\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            "document_count": self.collection.count(),
            "persist_directory": self.persist_directory,
            "collection_name": self.collection.name
        }


# Singleton instance
_rag_db: Optional[RAGDatabase] = None


def get_rag_database(persist_directory: str = "./data/chroma_db") -> Optional[RAGDatabase]:
    """
    Get or create the RAG database singleton.
    
    Returns None if ChromaDB is not available (graceful degradation).
    """
    global _rag_db
    
    if not CHROMADB_AVAILABLE:
        return None
    
    if _rag_db is None:
        try:
            _rag_db = RAGDatabase(persist_directory)
        except Exception as e:
            print(f"⚠️  Failed to initialize RAG database: {e}")
            print("   System will use hardcoded reference sources only.")
            return None
    
    return _rag_db


def get_reference_sources(risk_topic: str = "", use_rag: bool = True) -> str:
    """
    Get reference sources for risk assessment.
    
    HYBRID APPROACH:
    - RAG database provides dynamic, query-specific context (if available)
    - Hardcoded baseline sources ALWAYS included as fallback
    - System works even if RAG database is empty
    
    This ensures system works even if RAG database is empty,
    while allowing users to enhance with their own documents.
    
    Args:
        risk_topic: Optional topic to focus retrieval
        use_rag: Whether to attempt RAG retrieval (default: True)
        
    Returns:
        Formatted context string combining RAG results + hardcoded baseline
    """
    # Import hardcoded sources (always included)
    from src.utils.reference_sources import REFERENCE_SOURCES as HARDCODED_BASELINE
    
    parts = []
    
    # RAG section (if available and enabled)
    if use_rag:
        db = get_rag_database()
        if db and db.collection.count() > 0:
            parts.append("=== DYNAMIC REGULATORY CONTEXT (RAG Database) ===\n")
            if risk_topic:
                parts.append(db.get_context_for_assessment(risk_topic, n_docs=5))
            else:
                parts.append(db.get_context_for_assessment(
                    "IoT security risk assessment regulatory framework UK PSTI",
                    n_docs=5
                ))
            parts.append("\n" + "="*60 + "\n")
    
    # Hardcoded baseline (ALWAYS included)
    parts.append("=== BASELINE REFERENCE SOURCES ===\n")
    parts.append(HARDCODED_BASELINE)
    
    return "\n".join(parts)

