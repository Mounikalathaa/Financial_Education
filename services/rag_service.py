"""RAG Service for retrieving educational knowledge from vector store."""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import config

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval-Augmented Generation service using FAISS."""
    
    def __init__(self):
        """Initialize RAG service with vector store."""
        self.embedding_model = SentenceTransformer(config.embeddings.model)
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Try to load existing index
        self._load_index()
    
    def _load_index(self):
        """Load FAISS index and metadata from disk."""
        index_path = Path(config.vector_store.index_path)
        metadata_path = Path(config.vector_store.metadata_path)
        
        if index_path.exists() and metadata_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadata = data['metadata']
                logger.info(f"Loaded index with {len(self.documents)} documents")
            except Exception as e:
                logger.warning(f"Could not load index: {str(e)}")
                self._initialize_empty_index()
        else:
            logger.info("No existing index found, will create new one")
            self._initialize_empty_index()
    
    def _initialize_empty_index(self):
        """Initialize empty FAISS index."""
        dimension = config.embeddings.dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadata = []
    
    async def retrieve_knowledge(
        self, 
        concept: str, 
        difficulty: str,
        top_k: Optional[int] = None
    ) -> str:
        """
        Retrieve relevant knowledge from vector store.
        
        Args:
            concept: Financial concept to retrieve knowledge for
            difficulty: Difficulty level
            top_k: Number of documents to retrieve
            
        Returns:
            Combined knowledge text
        """
        top_k = top_k or config.vector_store.top_k
        
        logger.info(f"Retrieving knowledge for concept: {concept}, difficulty: {difficulty}")
        
        if not self.documents:
            logger.warning("No documents in index, returning default knowledge")
            return self._get_default_knowledge(concept, difficulty)
        
        try:
            # Create query
            query = f"{concept} {difficulty} financial education for children"
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            query_embedding = np.array([query_embedding]).astype('float32')
            
            # Search index
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            # Retrieve documents
            retrieved_docs = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    retrieved_docs.append(self.documents[idx])
            
            # Combine documents
            knowledge = "\n\n".join(retrieved_docs)
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            return knowledge
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
            return self._get_default_knowledge(concept, difficulty)
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]]):
        """
        Add documents to vector store.
        
        Args:
            documents: List of document texts
            metadata: List of metadata dictionaries
        """
        logger.info(f"Adding {len(documents)} documents to index")
        
        try:
            # Generate embeddings
            embeddings = self.embedding_model.encode(documents)
            embeddings = np.array(embeddings).astype('float32')
            
            # Add to index
            self.index.add(embeddings)
            self.documents.extend(documents)
            self.metadata.extend(metadata)
            
            logger.info(f"Successfully added documents. Total: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def save_index(self):
        """Save index and metadata to disk."""
        index_path = Path(config.vector_store.index_path)
        metadata_path = Path(config.vector_store.metadata_path)
        
        # Create directory if it doesn't exist
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata
                }, f)
            
            logger.info(f"Index saved to {index_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def _get_default_knowledge(self, concept: str, difficulty: str) -> str:
        """Return default knowledge when index is empty."""
        defaults = {
            "saving": """
Saving money means keeping some of your money safe instead of spending it all right away. 
When you save money, you can use it later for something special or important. It's like 
storing your favorite snacks for later instead of eating them all at once!

Why is saving important?
- It helps you buy bigger things you really want
- It keeps you prepared for surprises
- It helps your money grow over time
- It teaches you to make smart choices

Tips for saving:
- Put aside a little bit every time you get money
- Keep your savings in a safe place
- Think about what you're saving for
- Celebrate when you reach your saving goals
            """,
            "budgeting": """
A budget is a plan for your money. It helps you decide how to use your money wisely. 
Think of it like planning your homework time - you decide what to work on and when!

Creating a budget:
- Write down how much money you have
- List what you need to buy
- List what you want to buy
- Make sure you don't spend more than you have

A good budget helps you:
- Have money for things you need
- Save for things you want
- Avoid spending too much
- Feel in control of your money
            """,
            "needs_vs_wants": """
Needs are things you must have to live and be healthy. Wants are things that are nice 
to have but you can live without them.

Examples of NEEDS:
- Food and water
- A place to live
- Clothes to wear
- Medicine when you're sick

Examples of WANTS:
- Toys and games
- Candy and treats
- New video games
- Fancy clothes

Smart money choices mean taking care of needs first, then thinking about wants.
            """
        }
        
        return defaults.get(concept, f"Knowledge about {concept} for {difficulty} level learners.")
