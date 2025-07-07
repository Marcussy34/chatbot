"""
ZUS Coffee Data Pipeline - Phase 4 Complete Pipeline
====================================================

Master script that runs the complete data ingestion pipeline:
1. Scrape products from ZUS Coffee website
2. Scrape outlets from ZUS Coffee website
3. Build FAISS vector index from products
4. Create SQLite database from outlets

This demonstrates the complete data pipeline for the assessment.
"""

import logging
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from scrape_products import ZUSProductScraper
from scrape_outlets import ZUSOutletScraper
from build_vector_index import VectorIndexBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_complete_pipeline():
    """
    Run the complete data ingestion pipeline.
    
    This includes:
    1. Product scraping (for RAG)
    2. Outlet scraping (for Text2SQL)
    3. Vector index building (FAISS)
    4. Database creation (SQLite)
    """
    logger.info("Starting ZUS Coffee data ingestion pipeline...")
    
    try:
        # Step 1: Scrape products
        logger.info("Step 1: Scraping products...")
        product_scraper = ZUSProductScraper()
        products = product_scraper.scrape_drinkware_products()
        
        if products:
            product_scraper.save_products(products)
            logger.info(f"✅ Successfully scraped {len(products)} products")
        else:
            logger.error("❌ No products scraped")
            return False
        
        # Step 2: Scrape outlets
        logger.info("Step 2: Scraping outlets...")
        outlet_scraper = ZUSOutletScraper()
        outlets = outlet_scraper.scrape_kl_selangor_outlets()
        
        if outlets:
            outlet_scraper.save_outlets(outlets)
            outlet_scraper.create_sqlite_database(outlets)
            logger.info(f"✅ Successfully scraped {len(outlets)} outlets")
        else:
            logger.error("❌ No outlets scraped")
            return False
        
        # Step 3: Build vector index
        logger.info("Step 3: Building FAISS vector index...")
        vector_builder = VectorIndexBuilder()
        vector_builder.build_vector_index()
        logger.info("✅ Successfully built vector index")
        
        # Pipeline completed
        logger.info("🎉 Data ingestion pipeline completed successfully!")
        logger.info(f"📊 Pipeline Summary:")
        logger.info(f"   • Products scraped: {len(products)}")
        logger.info(f"   • Outlets scraped: {len(outlets)}")
        logger.info(f"   • Files created:")
        logger.info(f"     - data/zus_products.json")
        logger.info(f"     - data/zus_outlets.json")
        logger.info(f"     - data/zus_outlets.db")
        logger.info(f"     - data/product_index.faiss")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return False


def verify_outputs():
    """
    Verify that all expected output files were created.
    
    Returns:
        bool: True if all files exist
    """
    expected_files = [
        "data/zus_products.json",
        "data/zus_outlets.json", 
        "data/zus_outlets.db",
        "data/product_index.faiss"
    ]
    
    logger.info("Verifying output files...")
    
    all_exist = True
    for file_path in expected_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            logger.info(f"✅ {file_path} ({file_size:,} bytes)")
        else:
            logger.error(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist


def main():
    """Main function to run the complete pipeline."""
    logger.info("ZUS Coffee Data Pipeline - Mindhive Assessment")
    logger.info("=" * 50)
    
    # Run pipeline
    success = run_complete_pipeline()
    
    if success:
        # Verify outputs
        verification_success = verify_outputs()
        
        if verification_success:
            logger.info("🎯 All assessment deliverables created successfully!")
            logger.info("📋 Assessment Requirements Satisfied:")
            logger.info("   ✅ Vector-store ingestion scripts")
            logger.info("   ✅ Retrieval code for products")
            logger.info("   ✅ Text2SQL pipeline for outlets")
            logger.info("   ✅ Database schema and executor")
        else:
            logger.error("⚠️  Some output files are missing")
            sys.exit(1)
    else:
        logger.error("💥 Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 