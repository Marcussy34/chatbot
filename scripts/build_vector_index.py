"""
Build FAISS Vector Index - Phase 4
==================================

Creates FAISS vector index from scraped ZUS Coffee products for RAG.
This script ingests product data and builds embeddings for semantic search.

Required for assessment deliverable: "Vector-store ingestion scripts"
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorIndexBuilder:
    """
    Builds FAISS vector index from product data for semantic search.
    
    This is the ingestion script that creates embeddings from scraped
    product data and stores them in a FAISS index for efficient retrieval.
    """
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 products_file: str = "data/zus_products.json",
                 index_file: str = "data/product_index.faiss"):
        """
        Initialize the vector index builder.
        
        Args:
            model_name: SentenceTransformers model name
            products_file: Input products JSON file
            index_file: Output FAISS index file
        """
        self.model_name = model_name
        self.products_file = products_file
        self.index_file = index_file
        
        # Initialize sentence transformer
        logger.info(f"Loading SentenceTransformers model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def load_products(self) -> List[Dict[str, Any]]:
        """
        Load products from JSON file.
        
        Returns:
            List of product dictionaries
        """
        try:
            if not Path(self.products_file).exists():
                logger.error(f"Products file not found: {self.products_file}")
                return []
            
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            logger.info(f"Loaded {len(products)} products from {self.products_file}")
            return products
            
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            return []
    
    def create_product_texts(self, products: List[Dict[str, Any]]) -> List[str]:
        """
        Create text representations of products for embedding.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of text strings for embedding
        """
        product_texts = []
        
        for product in products:
            # Combine name, description, and price for rich context
            name = product.get('name', '')
            description = product.get('description', '')
            price = product.get('price', '')
            category = product.get('category', '')
            
            # Create comprehensive text representation
            text_parts = [name]
            if description:
                text_parts.append(description)
            if price:
                text_parts.append(price)
            if category:
                text_parts.append(category)
            
            product_text = ' '.join(text_parts)
            product_texts.append(product_text)
        
        logger.info(f"Created {len(product_texts)} product text representations")
        return product_texts
    
    def generate_embeddings(self, product_texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for product texts.
        
        Args:
            product_texts: List of text strings
            
        Returns:
            NumPy array of embeddings
        """
        logger.info("Generating embeddings for products...")
        
        try:
            # Generate embeddings in batches for efficiency
            embeddings = self.encoder.encode(
                product_texts, 
                convert_to_numpy=True,
                show_progress_bar=True,
                batch_size=32
            )
            
            logger.info(f"Generated embeddings shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return np.array([])
    
    def build_faiss_index(self, embeddings: np.ndarray) -> Optional[faiss.IndexFlatIP]:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: NumPy array of embeddings
            
        Returns:
            FAISS index or None if failed
        """
        try:
            logger.info("Building FAISS index...")
            
            # Create FAISS index (Inner Product for cosine similarity)
            index = faiss.IndexFlatIP(self.embedding_dim)
            
            # Normalize embeddings for cosine similarity
            embeddings_copy = embeddings.copy()
            faiss.normalize_L2(embeddings_copy)
            
            # Add embeddings to index
            index.add(embeddings_copy.astype(np.float32))
            
            logger.info(f"Built FAISS index with {index.ntotal} vectors")
            return index
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            return None
    
    def save_index(self, index: faiss.IndexFlatIP):
        """
        Save FAISS index to file.
        
        Args:
            index: FAISS index to save
        """
        try:
            # Ensure output directory exists
            Path(self.index_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Save index
            faiss.write_index(index, self.index_file)
            
            logger.info(f"Saved FAISS index to {self.index_file}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def build_vector_index(self):
        """
        Complete pipeline to build vector index from products.
        """
        logger.info("Starting vector index building pipeline...")
        
        # Load products
        products = self.load_products()
        if not products:
            logger.error("No products loaded. Cannot build index.")
            return
        
        # Create text representations
        product_texts = self.create_product_texts(products)
        if not product_texts:
            logger.error("No product texts created. Cannot build index.")
            return
        
        # Generate embeddings
        embeddings = self.generate_embeddings(product_texts)
        if embeddings.size == 0:
            logger.error("No embeddings generated. Cannot build index.")
            return
        
        # Build FAISS index
        index = self.build_faiss_index(embeddings)
        if index is None:
            logger.error("Failed to build FAISS index.")
            return
        
        # Save index
        self.save_index(index)
        
        logger.info("Vector index building completed successfully!")
        logger.info(f"Index contains {index.ntotal} product embeddings")
        logger.info(f"Embedding dimension: {self.embedding_dim}")
        logger.info(f"Model used: {self.model_name}")


def main():
    """Main function to build vector index."""
    builder = VectorIndexBuilder()
    builder.build_vector_index()


if __name__ == "__main__":
    main() 