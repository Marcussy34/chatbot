"""
SQL Service - Phase 4
=====================

Text2SQL service for ZUS Coffee outlet queries.
Translates natural language queries to SQL and executes them against
the SQLite outlets database.

Features:
- Natural language to SQL translation
- SQLite database integration
- Query validation and sanitization
- Structured result formatting
"""

import sqlite3
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class OutletSQLService:
    """
    SQL service for outlet queries using Text2SQL.
    
    Translates natural language queries to SQL and executes them
    against the ZUS Coffee outlets database.
    """
    
    def __init__(self, db_file: str = "data/zus_outlets.db"):
        """
        Initialize SQL service.
        
        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file
        
        # Database schema information
        self.schema_info = {
            'outlets': {
                'columns': ['id', 'name', 'address', 'phone', 'hours', 'area', 'services', 'scraped_at', 'created_at'],
                'description': 'ZUS Coffee outlets with location and service information'
            }
        }
        
        # Common query patterns and their SQL translations
        self.query_patterns = self._initialize_query_patterns()
        
        # Validate database connection
        self._validate_database()
    
    def _initialize_query_patterns(self) -> List[Dict[str, Any]]:
        """
        Initialize common query patterns for Text2SQL translation.
        
        Returns:
            List of query pattern dictionaries
        """
        return [
            {
                'pattern': r'outlets?\s+in\s+(.+)',
                'sql_template': "SELECT * FROM outlets WHERE LOWER(area) LIKE LOWER('%{location}%') OR LOWER(address) LIKE LOWER('%{location}%') OR LOWER(name) LIKE LOWER('%{location}%')",
                'description': 'Find outlets in a specific location'
            },
            {
                'pattern': r'opening\s+hours?\s+(.+)',
                'sql_template': "SELECT name, hours, address FROM outlets WHERE LOWER(name) LIKE LOWER('%{location}%') OR LOWER(area) LIKE LOWER('%{location}%')",
                'description': 'Get opening hours for outlets'
            },
            {
                'pattern': r'phone\s+number\s+(.+)',
                'sql_template': "SELECT name, phone, address FROM outlets WHERE name LIKE '%{location}%' OR area LIKE '%{location}%'",
                'description': 'Get phone numbers for outlets'
            },
            {
                'pattern': r'address\s+(.+)',
                'sql_template': "SELECT name, address FROM outlets WHERE name LIKE '%{location}%' OR area LIKE '%{location}%'",
                'description': 'Get addresses for outlets'
            },
            {
                'pattern': r'services?\s+(.+)',
                'sql_template': "SELECT name, services, address FROM outlets WHERE name LIKE '%{location}%' OR area LIKE '%{location}%'",
                'description': 'Get services for outlets'
            },
            {
                'pattern': r'all\s+outlets?',
                'sql_template': "SELECT name, area, address FROM outlets ORDER BY area, name",
                'description': 'List all outlets'
            },
            {
                'pattern': r'count\s+outlets?',
                'sql_template': "SELECT COUNT(*) as total_outlets FROM outlets",
                'description': 'Count total outlets'
            },
            {
                'pattern': r'(.+)\s+outlet',
                'sql_template': "SELECT * FROM outlets WHERE name LIKE '%{location}%' OR area LIKE '%{location}%'",
                'description': 'Find specific outlet'
            }
        ]
    
    def _validate_database(self):
        """Validate database connection and schema."""
        try:
            if not Path(self.db_file).exists():
                logger.error(f"Database file not found: {self.db_file}")
                return False
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM outlets")
                count = cursor.fetchone()[0]
                logger.info(f"Database validated: {count} outlets available")
                return True
                
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            return False
    
    def translate_to_sql(self, natural_query: str) -> Tuple[str, str]:
        """
        Translate natural language query to SQL.
        
        Args:
            natural_query: Natural language query
            
        Returns:
            Tuple of (SQL query, description)
        """
        try:
            query_lower = natural_query.lower().strip()
            
            # Try to match against known patterns
            for pattern_info in self.query_patterns:
                pattern = pattern_info['pattern']
                match = re.search(pattern, query_lower)
                
                if match:
                    # Extract location/parameter if present
                    if match.groups():
                        location = match.group(1).strip()
                        sql_query = pattern_info['sql_template'].format(location=location)
                    else:
                        sql_query = pattern_info['sql_template']
                    
                    return sql_query, pattern_info['description']
            
            # Default fallback for unmatched queries
            if any(keyword in query_lower for keyword in ['ss2', 'petaling', 'jaya', 'damansara', 'klcc', 'mont', 'kiara']):
                location = query_lower
                sql_query = f"SELECT * FROM outlets WHERE LOWER(area) LIKE LOWER('%{location}%') OR LOWER(address) LIKE LOWER('%{location}%') OR LOWER(name) LIKE LOWER('%{location}%')"
                return sql_query, "Search outlets by location"
            
            # Very general fallback
            sql_query = "SELECT name, area, address, hours FROM outlets ORDER BY area, name"
            return sql_query, "List all outlets (general query)"
            
        except Exception as e:
            logger.error(f"Error translating query: {e}")
            return "SELECT name, area, address FROM outlets LIMIT 5", "Default outlet listing"
    
    def execute_sql_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query against the database.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            List of result dictionaries
        """
        try:
            # Basic SQL injection protection
            if not self._is_safe_query(sql_query):
                logger.warning(f"Potentially unsafe query blocked: {sql_query}")
                return []
            
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()
                
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = [dict(row) for row in rows]
                
                logger.info(f"SQL query executed successfully: {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return []
    
    def _is_safe_query(self, sql_query: str) -> bool:
        """
        Basic SQL injection protection.
        
        Args:
            sql_query: SQL query to validate
            
        Returns:
            True if query appears safe
        """
        # Convert to lowercase for checking
        query_lower = sql_query.lower()
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'drop', 'delete', 'insert', 'update', 'alter', 'create',
            'truncate', 'exec', 'execute', 'union', '--', ';'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        # Must be a SELECT query
        if not query_lower.strip().startswith('select'):
            return False
        
        return True
    
    def query_outlets(self, natural_query: str) -> Dict[str, Any]:
        """
        Process natural language query and return results.
        
        Args:
            natural_query: Natural language query
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            # Translate to SQL
            sql_query, description = self.translate_to_sql(natural_query)
            
            # Execute query
            results = self.execute_sql_query(sql_query)
            
            # Format response
            response = {
                'original_query': natural_query,
                'sql_query': sql_query,
                'description': description,
                'results': results,
                'total_results': len(results),
                'timestamp': self._get_timestamp()
            }
            
            logger.info(f"Query processed: '{natural_query}' -> {len(results)} results")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'original_query': natural_query,
                'sql_query': '',
                'description': 'Error processing query',
                'results': [],
                'total_results': 0,
                'error': str(e),
                'timestamp': self._get_timestamp()
            }
    
    def format_results_for_user(self, query_result: Dict[str, Any]) -> str:
        """
        Format query results for user-friendly display.
        
        Args:
            query_result: Result from query_outlets()
            
        Returns:
            Formatted string for user display
        """
        try:
            results = query_result.get('results', [])
            original_query = query_result.get('original_query', '')
            
            if not results:
                return f"I couldn't find any outlets matching your query: '{original_query}'. Please try a different search or ask for all outlets."
            
            # Format based on number of results
            if len(results) == 1:
                outlet = results[0]
                response_parts = [f"Here's the information for {outlet.get('name', 'the outlet')}:"]
                
                if outlet.get('address'):
                    response_parts.append(f"📍 Address: {outlet['address']}")
                if outlet.get('hours'):
                    response_parts.append(f"🕒 Hours: {outlet['hours']}")
                if outlet.get('phone'):
                    response_parts.append(f"📞 Phone: {outlet['phone']}")
                if outlet.get('services'):
                    response_parts.append(f"🛍️ Services: {outlet['services']}")
                
                return "\n".join(response_parts)
            
            else:
                response_parts = [f"I found {len(results)} outlets for your query '{original_query}':"]
                
                for i, outlet in enumerate(results, 1):
                    name = outlet.get('name', f'Outlet {i}')
                    area = outlet.get('area', '')
                    address = outlet.get('address', '')
                    
                    outlet_info = f"\n{i}. **{name}**"
                    if area:
                        outlet_info += f" ({area})"
                    if address:
                        # Show shortened address
                        short_address = address.split(',')[0] if ',' in address else address
                        outlet_info += f"\n   📍 {short_address}"
                    if outlet.get('hours'):
                        outlet_info += f"\n   🕒 {outlet['hours']}"
                    
                    response_parts.append(outlet_info)
                
                response_parts.append("\nWould you like more details about any specific outlet?")
                return "\n".join(response_parts)
                
        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return f"I found some results for '{original_query}', but encountered an error formatting them. Please try again."
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_database_schema(self) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Returns:
            Schema information dictionary
        """
        return {
            'database': self.db_file,
            'tables': self.schema_info,
            'sample_queries': [
                "outlets in Petaling Jaya",
                "opening hours SS2",
                "phone number KLCC",
                "all outlets",
                "count outlets"
            ]
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status information.
        
        Returns:
            Service status dictionary
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM outlets")
                outlet_count = cursor.fetchone()[0]
                
                return {
                    'service': 'OutletSQLService',
                    'status': 'healthy',
                    'database': self.db_file,
                    'outlet_count': outlet_count,
                    'patterns_loaded': len(self.query_patterns)
                }
        except Exception as e:
            return {
                'service': 'OutletSQLService',
                'status': 'degraded',
                'database': self.db_file,
                'error': str(e),
                'patterns_loaded': len(self.query_patterns)
            }


def create_sql_service() -> OutletSQLService:
    """
    Factory function to create SQL service.
    
    Returns:
        Initialized OutletSQLService instance
    """
    return OutletSQLService()


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test SQL service
    sql_service = create_sql_service()
    
    # Test queries
    test_queries = [
        "outlets in Petaling Jaya",
        "opening hours SS2",
        "phone number KLCC",
        "all outlets"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        result = sql_service.query_outlets(query)
        formatted = sql_service.format_results_for_user(result)
        print(f"Results: {formatted}") 