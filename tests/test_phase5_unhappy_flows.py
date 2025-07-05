"""
Phase 5: Unhappy Flows Test Suite
================================

Comprehensive test suite for negative scenarios and robustness testing.
Tests three main categories:
1. Missing parameters
2. API downtime simulation
3. Malicious payload protection

Requirements:
- Clear error messages
- Recovery prompts
- No system crashes
- Graceful degradation
"""

import pytest
import httpx
from unittest.mock import patch, MagicMock
import sqlite3
import tempfile
import os
from pathlib import Path

from chatbot.planner import PlannerBot
from chatbot.tools import ToolManager, CalculatorTool, ProductSearchTool, OutletQueryTool
from app.main import app
from app.calculator import CalculatorService
from app.rag_service import ProductRAGService
from app.sql_service import OutletSQLService


class TestMissingParameters:
    """Test handling of missing or incomplete parameters."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = PlannerBot(enable_tools=True)
        self.tool_manager = ToolManager()
    
    def test_missing_calculation_expression(self):
        """Test calculator with missing expression."""
        test_cases = [
            "Calculate",
            "What's the result?",
            "Do some math",
            "Calculate something",
            "Can you calculate?"
        ]
        
        for query in test_cases:
            result = self.planner.execute_conversation_turn(query)
            
            # Should ask for clarification or provide helpful guidance
            response_lower = result['response'].lower()
            helpful_keywords = [
                'clarification', 'specify', 'what would you like', 
                'what calculation', 'which calculation', 'what math',
                'help', 'can i help', 'how can i'
            ]
            assert any(keyword in response_lower for keyword in helpful_keywords)
            
            # Should not crash
            assert 'response' in result
            assert 'decision' in result
    
    def test_missing_product_search_query(self):
        """Test product search with vague or missing query."""
        test_cases = [
            "Show products",
            "Find something",
            "What do you have?",
            "Search",
            "I want to buy"
        ]
        
        for query in test_cases:
            result = self.planner.execute_conversation_turn(query)
            
            # Should provide helpful response
            assert 'response' in result
            response = result['response'].lower()
            
            # Should either ask for clarification or provide general info
            assert any(keyword in response for keyword in [
                'what type', 'specify', 'looking for', 'help you find',
                'drinkware', 'products available'
            ])
    
    def test_missing_outlet_location(self):
        """Test outlet query with missing location information."""
        test_cases = [
            "Show outlets",
            "Where are your stores?",
            "Find a location",
            "I need an outlet",
            "Store hours"
        ]
        
        for query in test_cases:
            result = self.planner.execute_conversation_turn(query)
            
            # Should provide helpful response
            assert 'response' in result
            response = result['response'].lower()
            
            # Should either show all outlets or ask for location
            helpful_keywords = [
                'all outlets', 'which area', 'specific location',
                'where would you like', 'available locations',
                'outlet information', 'help you with outlet',
                'can ask about', 'locations', 'opening times',
                'i\'d be happy to help', 'happy to help',
                'i found', 'outlets for your query', 'would you like more details',
                'ask for all outlets', 'try a different search'
            ]
            assert any(keyword in response for keyword in helpful_keywords)
    
    def test_empty_inputs(self):
        """Test completely empty inputs."""
        empty_inputs = ["", "   ", "\n", "\t"]
        
        for empty_input in empty_inputs:
            result = self.planner.execute_conversation_turn(empty_input)
            
            # Should handle gracefully
            assert 'response' in result
            assert len(result['response']) > 0
            
            # Should ask for input or provide help
            response = result['response'].lower()
            assert any(keyword in response for keyword in [
                'help', 'ask', 'can i', 'what would you like'
            ])


class TestAPIDowntime:
    """Test handling of API downtime and service unavailability."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool_manager = ToolManager()
        self.planner = PlannerBot(enable_tools=True)
    
    @patch('httpx.Client.get')
    def test_calculator_api_downtime(self, mock_get):
        """Test calculator tool when API is down."""
        # Simulate connection error
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        calculator_tool = CalculatorTool()
        result = calculator_tool.run("2 + 3")
        
        # Should handle gracefully
        assert "unavailable" in result.lower()
        assert "service" in result.lower()
        assert "2 + 3" in result  # Should mention the expression
        
        # Should not crash
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('httpx.Client.get')
    def test_calculator_api_timeout(self, mock_get):
        """Test calculator tool timeout."""
        # Simulate timeout
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        
        calculator_tool = CalculatorTool()
        result = calculator_tool.run("10 * 5")
        
        # Should handle timeout gracefully
        assert "timed out" in result.lower()
        assert "10 * 5" in result
        assert isinstance(result, str)
    
    @patch('httpx.Client.get')
    def test_calculator_api_500_error(self, mock_get):
        """Test calculator API returning HTTP 500."""
        # Mock 500 error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.headers = {"content-type": "application/json"}
        mock_get.return_value = mock_response
        
        calculator_tool = CalculatorTool()
        result = calculator_tool.run("7 + 8")
        
        # Should handle HTTP errors gracefully
        assert "error" in result.lower()
        assert "7 + 8" in result
        assert isinstance(result, str)
    
    @patch('httpx.Client.get')
    def test_product_search_api_downtime(self, mock_get):
        """Test product search when API is down."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        product_tool = ProductSearchTool()
        result = product_tool.run("black tumbler")
        
        # Should handle gracefully
        assert "unavailable" in result.lower()
        assert "black tumbler" in result
        assert isinstance(result, str)
    
    @patch('httpx.Client.get')
    def test_outlet_query_api_downtime(self, mock_get):
        """Test outlet query when API is down."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        outlet_tool = OutletQueryTool()
        result = outlet_tool.run("outlets in SS2")
        
        # Should handle gracefully
        assert "unavailable" in result.lower()
        assert "outlets in SS2" in result
        assert isinstance(result, str)
    
    def test_planner_with_all_apis_down(self):
        """Test planner behavior when all APIs are down."""
        with patch('httpx.Client.get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("All services down")
            
            # Test different types of queries
            queries = [
                "What's 5 + 5?",
                "Find black tumbler",
                "Outlets in Petaling Jaya"
            ]
            
            for query in queries:
                result = self.planner.execute_conversation_turn(query)
                
                # Should still respond without crashing
                assert 'response' in result
                assert 'decision' in result
                
                # Should indicate service issues
                response = result['response'].lower()
                assert any(keyword in response for keyword in [
                    'unavailable', 'down', 'error', 'try again'
                ])


class TestMaliciousPayloads:
    """Test protection against malicious inputs and security vulnerabilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator_service = CalculatorService()
        self.sql_service = OutletSQLService()
        self.planner = PlannerBot(enable_tools=True)
    
    def test_sql_injection_attempts(self):
        """Test SQL injection protection in outlet queries."""
        sql_injection_attempts = [
            "outlets'; DROP TABLE outlets; --",
            "outlets' OR '1'='1",
            "outlets'; DELETE FROM outlets; --",
            "outlets' UNION SELECT * FROM users --",
            "outlets'; INSERT INTO outlets VALUES ('hack'); --",
            "outlets'; UPDATE outlets SET name='hacked'; --",
            "outlets'; CREATE TABLE hack AS SELECT * FROM outlets; --",
            "outlets' AND 1=1 UNION SELECT password FROM users --"
        ]
        
        for malicious_query in sql_injection_attempts:
            # Test direct SQL service
            result = self.sql_service.query_outlets(malicious_query)
            
            # Should block or sanitize malicious queries
            assert result['total_results'] == 0 or \
                   'error' in result or \
                   result['results'] == []
            
            # Test through planner
            planner_result = self.planner.execute_conversation_turn(malicious_query)
            
            # Should not crash and should provide safe response
            assert 'response' in planner_result
            response = planner_result['response'].lower()
            
            # Should not execute dangerous operations (check for actual execution, not echoing)
            dangerous_execution_indicators = [
                'table dropped', 'data deleted', 'records inserted', 
                'table created', 'password', 'users table', 'hack successful'
            ]
            assert not any(indicator in response for indicator in dangerous_execution_indicators)
            
            # Should provide safe, helpful response
            safe_response_indicators = [
                'couldn\'t find', 'try a different search', 'ask for all outlets',
                'no results', 'error', 'invalid'
            ]
            assert any(indicator in response for indicator in safe_response_indicators)
    
    def test_calculator_code_injection(self):
        """Test calculator protection against code injection."""
        code_injection_attempts = [
            "__import__('os').system('rm -rf /')",
            "eval('print(\"hacked\")')",
            "exec('import os; os.system(\"ls\")')",
            "open('/etc/passwd', 'r').read()",
            "globals()",
            "locals()",
            "__builtins__",
            "1; import os; os.system('echo hacked')",
            "print('injection')",
            "lambda: __import__('os')"
        ]
        
        for malicious_expr in code_injection_attempts:
            # Should raise ValueError for dangerous patterns
            with pytest.raises(ValueError):
                self.calculator_service.evaluate_expression(malicious_expr)
            
            # Test through planner
            result = self.planner.execute_conversation_turn(f"Calculate {malicious_expr}")
            
            # Should handle safely
            assert 'response' in result
            response = result['response'].lower()
            assert any(keyword in response for keyword in [
                'invalid', 'error', 'dangerous', 'not allowed'
            ])
    
    def test_xss_attempts_in_queries(self):
        """Test protection against XSS-like payloads in queries."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<svg onload=alert('xss')>",
            "&#60;script&#62;alert('xss')&#60;/script&#62;"
        ]
        
        for xss_payload in xss_attempts:
            # Test product search
            result = self.planner.execute_conversation_turn(f"Find {xss_payload}")
            
            # Should handle safely without executing scripts
            assert 'response' in result
            response = result['response']
            
            # Should not contain executable script tags
            assert '<script>' not in response
            assert 'javascript:' not in response
            assert 'onerror=' not in response
    
    def test_large_payload_handling(self):
        """Test handling of extremely large inputs."""
        # Create very large input
        large_input = "A" * 10000  # 10KB string
        very_large_input = "B" * 100000  # 100KB string
        
        test_cases = [
            f"Calculate {large_input}",
            f"Find products {large_input}",
            f"Outlets in {large_input}",
            very_large_input
        ]
        
        for large_query in test_cases:
            # Should handle without crashing
            result = self.planner.execute_conversation_turn(large_query)
            
            assert 'response' in result
            assert 'decision' in result
            
            # Should provide reasonable response
            response = result['response']
            assert len(response) < 5000  # Response should be reasonable size
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        special_inputs = [
            "Calculate 2 + 3 \x00 null byte",
            "Find products with emoji 🔥☕️💀",
            "Outlets in location with unicode: café naïve résumé",
            "Query with control chars: \x01\x02\x03",
            "Mixed encoding: ½ × ¾ = ⅜",
            "Zalgo text: ḧ̸̢̧̰̝̠̱̖̺̭̰̫̻̼̮̯̖̰̙̘̫́̈́̽̈́̃̈́̽̈́̈́̈́̈́̈́̈́ë̸̢̧̛̝̠̱̖̺̭̰̫̻̼̮̯̖̰̙̘̫́̈́̽̈́̃̈́̽̈́̈́̈́̈́̈́̈́l̸̢̧̛̝̠̱̖̺̭̰̫̻̼̮̯̖̰̙̘̫̈́̈́̽̈́̃̈́̽̈́̈́̈́̈́̈́̈́l̸̢̧̛̝̠̱̖̺̭̰̫̻̼̮̯̖̰̙̘̫̈́̈́̽̈́̃̈́̽̈́̈́̈́̈́̈́̈́ơ̸̢̧̝̠̱̖̺̭̰̫̻̼̮̯̖̰̙̘̫̈́̈́̽̈́̃̈́̽̈́̈́̈́̈́̈́̈́"
        ]
        
        for special_input in special_inputs:
            # Should handle without crashing
            result = self.planner.execute_conversation_turn(special_input)
            
            assert 'response' in result
            assert isinstance(result['response'], str)
            
            # Should not crash the system
            assert len(result['response']) > 0


class TestRecoveryAndGracefulDegradation:
    """Test system recovery and graceful degradation capabilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = PlannerBot(enable_tools=True)
    
    def test_partial_service_degradation(self):
        """Test behavior when some services are down but others work."""
        with patch('httpx.Client.get') as mock_get:
            def mock_response(*args, **kwargs):
                url = args[0]
                if 'calculator' in url:
                    # Calculator works
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = {"result": 42}
                    return response
                else:
                    # Other services are down
                    raise httpx.ConnectError("Service down")
            
            mock_get.side_effect = mock_response
            
            # Test mixed queries
            calc_result = self.planner.execute_conversation_turn("What's 6 * 7?")
            product_result = self.planner.execute_conversation_turn("Find black mug")
            
            # Calculator should work
            assert 'response' in calc_result
            assert '42' in calc_result['response']
            
            # Product search should fail gracefully
            assert 'response' in product_result
            assert 'unavailable' in product_result['response'].lower()
    
    def test_recovery_prompts(self):
        """Test that system provides helpful recovery prompts."""
        error_scenarios = [
            ("", "Empty input"),
            ("asdfghjkl", "Nonsense input"),
            ("Calculate nothing", "Vague calculation"),
            ("Find stuff", "Vague product search")
        ]
        
        for query, scenario in error_scenarios:
            result = self.planner.execute_conversation_turn(query)
            
            # Should provide helpful guidance
            assert 'response' in result
            response = result['response'].lower()
            
            # Should contain helpful suggestions
            helpful_keywords = [
                'try', 'example', 'help', 'can i', 'would you like',
                'specify', 'such as', 'for instance'
            ]
            
            assert any(keyword in response for keyword in helpful_keywords)
    
    def test_system_never_crashes(self):
        """Stress test to ensure system never crashes."""
        stress_inputs = [
            None,  # This should be handled before reaching planner
            "",
            "   ",
            "\n\n\n",
            "🚀" * 100,
            "Calculate " + "(" * 100 + "1" + ")" * 100,
            "Find " + "a" * 1000,
            "Outlets in " + "location" * 50,
            "What's " + "1+" * 100 + "1",
            "Show me " + "products " * 100
        ]
        
        for stress_input in stress_inputs:
            if stress_input is None:
                continue
                
            try:
                result = self.planner.execute_conversation_turn(stress_input)
                
                # Should always return valid response structure
                assert isinstance(result, dict)
                assert 'response' in result
                assert 'decision' in result
                assert isinstance(result['response'], str)
                
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"System crashed with input '{stress_input}': {e}")


class TestSecurityStrategy:
    """Test overall security strategy implementation."""
    
    def test_input_sanitization(self):
        """Test that inputs are properly sanitized."""
        # Test calculator input sanitization
        calc_service = CalculatorService()
        
        # Should reject dangerous patterns
        with pytest.raises(ValueError):
            calc_service.evaluate_expression("__import__")
        
        with pytest.raises(ValueError):
            calc_service.evaluate_expression("eval(")
    
    def test_sql_query_validation(self):
        """Test SQL query validation."""
        sql_service = OutletSQLService()
        
        # Test dangerous queries are blocked
        dangerous_queries = [
            "DROP TABLE outlets",
            "DELETE FROM outlets",
            "INSERT INTO outlets VALUES",
            "UPDATE outlets SET",
            "UNION SELECT * FROM"
        ]
        
        for dangerous_query in dangerous_queries:
            assert not sql_service._is_safe_query(dangerous_query)
    
    def test_error_message_security(self):
        """Test that error messages don't leak sensitive information."""
        # Test that database errors don't expose schema
        sql_service = OutletSQLService()
        
        # Create invalid query that would normally expose database info
        result = sql_service.query_outlets("SELECT * FROM nonexistent_table")
        
        # Should not expose database schema in error
        assert 'sqlite' not in str(result).lower()
        assert 'database' not in str(result).lower()
        assert 'schema' not in str(result).lower()
        
        # Should provide generic error message
        assert result['total_results'] == 0


# Integration test for complete unhappy flow scenarios
class TestEndToEndUnhappyFlows:
    """End-to-end tests for complete unhappy flow scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = PlannerBot(enable_tools=True)
    
    def test_complete_service_outage_scenario(self):
        """Test complete service outage handling."""
        with patch('httpx.Client.get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("All services down")
            
            # User tries multiple types of queries
            queries = [
                "What's 10 + 5?",
                "Find ceramic mug",
                "Outlets in KLCC",
                "Calculate 2 * 3",
                "Show products",
                "Store locations"
            ]
            
            for query in queries:
                result = self.planner.execute_conversation_turn(query)
                
                # Should handle all failures gracefully
                assert 'response' in result
                response = result['response'].lower()
                
                # Should indicate service issues and suggest retry
                assert any(keyword in response for keyword in [
                    'unavailable', 'down', 'try again', 'later'
                ])
                
                # Should not crash or return empty response
                assert len(result['response']) > 10
    
    def test_malicious_user_session(self):
        """Test handling of a malicious user trying multiple attack vectors."""
        malicious_queries = [
            "Calculate __import__('os').system('rm -rf /')",
            "outlets'; DROP TABLE outlets; --",
            "Find <script>alert('xss')</script>",
            "What's " + "A" * 10000,
            "Outlets in '; DELETE FROM users; --",
            "Calculate eval('malicious_code')"
        ]
        
        for malicious_query in malicious_queries:
            result = self.planner.execute_conversation_turn(malicious_query)
            
            # Should handle all malicious inputs safely
            assert 'response' in result
            
            # Should not execute malicious code
            response = result['response']
            assert 'rm -rf' not in response
            assert 'DELETE FROM' not in response
            assert '<script>' not in response
            assert 'malicious_code' not in response
            
            # Should provide safe error messages
            assert any(keyword in response.lower() for keyword in [
                'invalid', 'error', 'not allowed', 'cannot'
            ])


if __name__ == "__main__":
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1:
        category = sys.argv[1]
        if category == "missing":
            pytest.main(["-v", "TestMissingParameters"])
        elif category == "downtime":
            pytest.main(["-v", "TestAPIDowntime"])
        elif category == "malicious":
            pytest.main(["-v", "TestMaliciousPayloads"])
        elif category == "security":
            pytest.main(["-v", "TestSecurityStrategy"])
        else:
            pytest.main(["-v", __file__])
    else:
        pytest.main(["-v", __file__]) 