"""
RAG Service - Phase 4
=====================

RAG (Retrieval-Augmented Generation) service for ZUS Coffee product search.
Uses FAISS vector store for efficient similarity search and generates
AI-powered summaries of relevant products.

Features:
- FAISS vector store with sentence transformers
- Product embedding and indexing
- Top-k retrieval with similarity scoring
- AI-generated summaries of search results
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

# Vector store and embeddings
import faiss
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger(__name__)


class ProductRAGService:
    """
    RAG service for product search and retrieval.
    
    Provides semantic search over ZUS Coffee drinkware products
    with AI-generated summaries.
    """
    
    def __init__(self, 
                 products_file: str = "data/zus_products.json",
                 model_name: str = "all-MiniLM-L6-v2",
                 index_file: str = "data/product_index.faiss"):
        """
        Initialize RAG service.
        
        Args:
            products_file: Path to products JSON file
            model_name: Sentence transformer model name
            index_file: Path to FAISS index file
        """
        self.products_file = products_file
        self.model_name = model_name
        self.index_file = index_file
        
        # Initialize sentence transformer
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        
        # Storage for products and embeddings
        self.products: List[Dict[str, Any]] = []
        self.index: Optional[faiss.IndexFlatIP] = None
        
        # Load products and build index
        self._load_products()
        self._build_or_load_index()
    
    def _load_products(self):
        """Load products from JSON file."""
        try:
            if Path(self.products_file).exists():
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"Loaded {len(self.products)} products from {self.products_file}")
            else:
                logger.warning(f"Products file not found: {self.products_file}")
                self.products = []
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            self.products = []
    
    def _build_or_load_index(self):
        """Build or load FAISS index for products."""
        try:
            # Try to load existing index
            if Path(self.index_file).exists():
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Loaded existing FAISS index from {self.index_file}")
                return
            
            # Build new index if products available
            if not self.products:
                logger.warning("No products available to build index")
                return
            
            logger.info("Building new FAISS index...")
            self._build_index()
            
        except Exception as e:
            logger.error(f"Error building/loading index: {e}")
            self.index = None
    
    def _build_index(self):
        """Build FAISS index from products."""
        try:
            # Create product texts for embedding
            product_texts = []
            for product in self.products:
                # Combine name, description, and price for rich context
                text = f"{product['name']} {product['description']} {product['price']}"
                product_texts.append(text)
            
            # Generate embeddings
            logger.info("Generating embeddings for products...")
            embeddings = self.encoder.encode(product_texts, convert_to_numpy=True)
            
            # Create FAISS index (Inner Product for cosine similarity)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            self.index.add(embeddings.astype(np.float32))
            
            # Save index
            Path(self.index_file).parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, self.index_file)
            
            logger.info(f"Built and saved FAISS index with {len(self.products)} products")
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            self.index = None
    
    def search_products(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of product dictionaries with similarity scores
        """
        try:
            if not self.index or not self.products:
                logger.warning("Index or products not available")
                return []
            
            # Generate query embedding
            query_embedding = self.encoder.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search index
            scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.products):
                    product = self.products[idx].copy()
                    product['similarity_score'] = float(score)
                    product['rank'] = i + 1
                    results.append(product)
            
            logger.info(f"Found {len(results)} products for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def generate_summary(self, query: str, products: List[Dict[str, Any]]) -> str:
        """
        Generate AI summary of search results.
        
        Args:
            query: Original search query
            products: List of relevant products
            
        Returns:
            Generated summary text
        """
        try:
            if not products:
                return f"I couldn't find any drinkware products matching '{query}'. Please try a different search term or browse our available items."
            
            # Create summary based on products
            summary_parts = [
                f"Based on your search for '{query}', I found {len(products)} relevant drinkware products:"
            ]
            
            for i, product in enumerate(products, 1):
                price = product.get('price', 'Price not available')
                name = product.get('name', 'Unknown product')
                description = product.get('description', '')
                
                # Create product summary
                product_summary = f"\n{i}. **{name}** - {price}"
                if description:
                    # Truncate long descriptions
                    desc_preview = description[:100] + "..." if len(description) > 100 else description
                    product_summary += f"\n   {desc_preview}"
                
                summary_parts.append(product_summary)
            
            # Add recommendation
            if len(products) == 1:
                summary_parts.append(f"\nThis {products[0]['name']} seems perfect for your needs!")
            else:
                summary_parts.append(f"\nAll of these options are great for coffee lovers. The {products[0]['name']} is our top recommendation based on your search.")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"I found some products for '{query}', but encountered an error generating the summary. Please try again."
    
    def get_product_recommendations(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Get product recommendations with AI-generated summary.
        
        Args:
            query: Search query
            top_k: Number of recommendations
            
        Returns:
            Dictionary with products and summary
        """
        try:
            # Search for products
            products = self.search_products(query, top_k)
            
            # Generate summary
            summary = self.generate_summary(query, products)
            
            return {
                'query': query,
                'summary': summary,
                'products': products,
                'total_found': len(products),
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                'query': query,
                'summary': f"Sorry, I encountered an error while searching for '{query}'. Please try again.",
                'products': [],
                'total_found': 0,
                'timestamp': self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status information.
        
        Returns:
            Service status dictionary
        """
        return {
            'service': 'ProductRAGService',
            'status': 'healthy' if self.index is not None else 'degraded',
            'products_loaded': len(self.products),
            'index_available': self.index is not None,
            'model': self.model_name,
            'embedding_dim': self.embedding_dim
        }


def create_rag_service() -> ProductRAGService:
    """
    Factory function to create RAG service.
    
    Returns:
        Initialized ProductRAGService instance
    """
    return ProductRAGService()


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test RAG service
    rag = create_rag_service()
    
    # Test search
    test_queries = ["black tumbler", "ceramic mug", "travel bottle"]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        result = rag.get_product_recommendations(query)
        print(f"Summary: {result['summary']}")
        print(f"Products found: {result['total_found']}") 