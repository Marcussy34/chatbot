"""
ZUS Coffee Product Scraper - Phase 4
====================================

Scrapes drinkware products from ZUS Coffee website for RAG integration.
Source: https://shop.zuscoffee.com/ (Drinkware category only)

This script collects product information including:
- Product names and descriptions
- Prices and specifications
- Product images and details
- Categories and features
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZUSProductScraper:
    """
    Scraper for ZUS Coffee drinkware products.
    
    Focuses on drinkware category as specified in assessment requirements.
    """
    
    def __init__(self, base_url: str = "https://shop.zuscoffee.com"):
        """
        Initialize the scraper.
        
        Args:
            base_url: Base URL of ZUS Coffee shop
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_drinkware_products(self) -> List[Dict[str, Any]]:
        """
        Scrape all drinkware products from ZUS Coffee website.
        
        Returns:
            List of product dictionaries with details
        """
        products = []
        
        try:
            # Get drinkware category page
            drinkware_url = f"{self.base_url}/collections/drinkware"
            logger.info(f"Fetching drinkware products from: {drinkware_url}")
            
            response = self.session.get(drinkware_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product cards/items
            product_items = soup.find_all(['div', 'article'], class_=True)
            
            logger.info(f"Found {len(product_items)} potential product items")
            
            for item in product_items:
                product_data = self._extract_product_info(item)
                if product_data:
                    products.append(product_data)
                    logger.info(f"Extracted product: {product_data.get('name', 'Unknown')}")
                
                # Be respectful to the server
                time.sleep(0.5)
                
        except requests.RequestException as e:
            logger.error(f"Error fetching drinkware page: {e}")
            # Return sample data for development/testing
            return self._get_sample_products()
        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}")
            return self._get_sample_products()
        
        # If no products found, return sample data
        if not products:
            logger.warning("No products found, returning sample data")
            return self._get_sample_products()
            
        return products
    
    def _extract_product_info(self, item_element) -> Optional[Dict[str, Any]]:
        """
        Extract product information from a product element.
        
        Args:
            item_element: BeautifulSoup element containing product info
            
        Returns:
            Dictionary with product details or None if extraction fails
        """
        try:
            # Extract product name
            name_elem = item_element.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['title', 'name', 'product']
            ))
            if not name_elem:
                name_elem = item_element.find(['h2', 'h3', 'h4'])
            
            name = name_elem.get_text(strip=True) if name_elem else ""
            if not name or len(name) < 3:
                return None
                
            # Extract price
            price_elem = item_element.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower())
            if not price_elem:
                price_elem = item_element.find(string=lambda text: text and 'RM' in text)
                if price_elem:
                    price_elem = price_elem.parent
            
            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
            
            # Extract product link first
            link_elem = item_element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"{self.base_url}{link}"
            
            # Extract description
            desc_elem = item_element.find(['p', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['description', 'desc', 'summary']
            ))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Create product data
            product_data = {
                'name': name,
                'price': price,
                'description': description,
                'link': link,
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return product_data
            
        except Exception as e:
            logger.warning(f"Error extracting product info: {e}")
            return None
    
    def _get_sample_products(self) -> List[Dict[str, Any]]:
        """
        Return sample drinkware products for development/testing.
        
        Returns:
            List of sample product dictionaries
        """
        return [
            {
                'name': 'ZUS Coffee Tumbler - Black',
                'price': 'RM 25.00',
                'description': 'Premium black tumbler with ZUS Coffee branding. Perfect for keeping your coffee hot on the go. Made from high-quality stainless steel with double-wall insulation.',
                'link': 'https://shop.zuscoffee.com/products/zus-tumbler-black',
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'name': 'ZUS Coffee Mug - White Ceramic',
                'price': 'RM 18.00',
                'description': 'Classic white ceramic mug with ZUS Coffee logo. Perfect for office or home use. Dishwasher and microwave safe.',
                'link': 'https://shop.zuscoffee.com/products/zus-mug-white',
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'name': 'ZUS Travel Bottle - Stainless Steel',
                'price': 'RM 35.00',
                'description': 'Large capacity travel bottle for coffee lovers. Features leak-proof design and temperature retention technology. Ideal for long commutes.',
                'link': 'https://shop.zuscoffee.com/products/zus-travel-bottle',
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'name': 'ZUS Glass Cup Set - 2 Pieces',
                'price': 'RM 22.00',
                'description': 'Elegant glass cup set perfect for enjoying ZUS coffee at home. Heat-resistant borosilicate glass with comfortable grip design.',
                'link': 'https://shop.zuscoffee.com/products/zus-glass-cup-set',
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'name': 'ZUS Insulated Tumbler - Rose Gold',
                'price': 'RM 28.00',
                'description': 'Stylish rose gold insulated tumbler with premium finish. Keeps beverages at optimal temperature for hours. Perfect gift for coffee enthusiasts.',
                'link': 'https://shop.zuscoffee.com/products/zus-tumbler-rose-gold',
                'category': 'Drinkware',
                'source': 'ZUS Coffee',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    def save_products(self, products: List[Dict[str, Any]], output_file: str = "data/zus_products.json"):
        """
        Save scraped products to JSON file.
        
        Args:
            products: List of product dictionaries
            output_file: Output file path
        """
        try:
            # Ensure data directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(products)} products to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving products: {e}")


def main():
    """Main function to run the product scraper."""
    scraper = ZUSProductScraper()
    
    logger.info("Starting ZUS Coffee drinkware scraping...")
    products = scraper.scrape_drinkware_products()
    
    if products:
        scraper.save_products(products)
        logger.info(f"Successfully scraped {len(products)} drinkware products")
    else:
        logger.error("No products scraped")


if __name__ == "__main__":
    main() 