"""
Test Suite for Phase 3: Calculator Tool Integration
==================================================

This test suite validates the calculator API, tool integration,
and end-to-end functionality including error handling.

Test Coverage:
- Calculator service functionality
- FastAPI endpoint testing
- LangChain tool integration
- Error handling and edge cases
- Integration with planner system
"""

import pytest
import sys
import os
import httpx
from unittest.mock import patch, MagicMock
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.calculator import CalculatorService, calculate
from chatbot.tools import CalculatorTool, ToolManager, calculate_expression
from chatbot.planner import PlannerBot


class TestCalculatorService:
    """Test suite for the core CalculatorService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.calculator = CalculatorService()
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        test_cases = [
            ("2 + 3", 5),
            ("10 - 4", 6),
            ("5 * 6", 30),
            ("15 / 3", 5.0),
            ("2 ** 3", 8),
            ("10 % 3", 1),
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.evaluate_expression(expression)
            assert result == expected, f"Expected {expected} for {expression}, got {result}"
    
    def test_order_of_operations(self):
        """Test that order of operations is respected."""
        test_cases = [
            ("2 + 3 * 4", 14),  # Should be 2 + 12 = 14, not 5 * 4 = 20
            ("(2 + 3) * 4", 20),  # Should be 5 * 4 = 20
            ("10 - 2 * 3", 4),   # Should be 10 - 6 = 4
            ("(10 - 2) * 3", 24), # Should be 8 * 3 = 24
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.evaluate_expression(expression)
            assert result == expected, f"Expected {expected} for {expression}, got {result}"
    
    def test_decimal_numbers(self):
        """Test calculations with decimal numbers."""
        test_cases = [
            ("2.5 + 3.5", 6.0),
            ("10.5 / 2", 5.25),
            ("3.14 * 2", 6.28),
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.evaluate_expression(expression)
            assert abs(result - expected) < 0.0001, f"Expected {expected} for {expression}, got {result}"
    
    def test_negative_numbers(self):
        """Test calculations with negative numbers."""
        test_cases = [
            ("-5 + 3", -2),
            ("10 + (-4)", 6),
            ("-2 * 3", -6),
            ("(-5) ** 2", 25),
        ]
        
        for expression, expected in test_cases:
            result = self.calculator.evaluate_expression(expression)
            assert result == expected, f"Expected {expected} for {expression}, got {result}"
    
    def test_division_by_zero(self):
        """Test that division by zero raises appropriate error."""
        with pytest.raises(ZeroDivisionError):
            self.calculator.evaluate_expression("10 / 0")
        
        with pytest.raises(ZeroDivisionError):
            self.calculator.evaluate_expression("5 % 0")
    
    def test_invalid_expressions(self):
        """Test that invalid expressions raise appropriate errors."""
        invalid_expressions = [
            "",           # Empty expression
            "   ",        # Whitespace only
            "2 +",        # Incomplete expression
            "2 + + 3",    # Invalid syntax
            "abc",        # Non-numeric
            "2 & 3",      # Unsupported operator
            "import os",  # Dangerous pattern
        ]
        
        for expr in invalid_expressions:
            with pytest.raises(ValueError):
                self.calculator.evaluate_expression(expr)
    
    def test_expression_normalization(self):
        """Test that expressions are normalized correctly."""
        test_cases = [
            ("2^3", "2**3"),     # ^ to **
            ("2×3", "2*3"),      # × to *
            ("6÷2", "6/2"),      # ÷ to /
            ("  2  +  3  ", "2 + 3"),  # Whitespace normalization
        ]
        
        for original, expected_normalized in test_cases:
            normalized = self.calculator._normalize_expression(original)
            # Test that both expressions give the same result
            result1 = self.calculator.evaluate_expression(original)
            result2 = self.calculator.evaluate_expression(expected_normalized)
            assert result1 == result2
    
    def test_convenience_function(self):
        """Test the convenience calculate function."""
        result = calculate("2 + 3")
        assert result == 5


class TestCalculatorTool:
    """Test suite for the LangChain CalculatorTool integration."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tool = CalculatorTool(base_url="http://localhost:8000")
    
    def test_tool_properties(self):
        """Test that tool has correct properties."""
        assert self.tool.name == "calculator"
        assert "mathematical expressions" in self.tool.description.lower()
        assert self.tool.return_direct is False
    
    @patch('httpx.Client.get')
    def test_successful_calculation(self, mock_get):
        """Test successful calculation through tool."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 5}
        mock_get.return_value = mock_response
        
        result = self.tool.run("2+3")
        
        assert "result of 2+3 is 5" in result.lower()
        mock_get.assert_called_once()
    
    @patch('httpx.Client.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling in tool."""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid expression"}
        mock_response.headers = {"content-type": "application/json"}
        mock_get.return_value = mock_response
        
        result = self.tool.run("invalid")
        
        assert "error calculating" in result.lower()
        assert "invalid expression" in result.lower()
    
    @patch('httpx.Client.get')
    def test_connection_error_handling(self, mock_get):
        """Test connection error handling in tool."""
        # Mock connection error
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        result = self.tool.run("2+3")
        
        assert "service is currently unavailable" in result.lower()
    
    @patch('httpx.Client.get')
    def test_timeout_error_handling(self, mock_get):
        """Test timeout error handling in tool."""
        # Mock timeout error
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        
        result = self.tool.run("2+3")
        
        assert "service timed out" in result.lower()


class TestToolManager:
    """Test suite for the ToolManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.manager = ToolManager()
    
    def test_tool_manager_initialization(self):
        """Test that tool manager initializes correctly."""
        assert self.manager is not None
        assert "calculator" in self.manager.get_all_tools()
    
    def test_get_tool(self):
        """Test getting tools by name."""
        calculator = self.manager.get_tool("calculator")
        assert calculator is not None
        assert calculator.name == "calculator"
        
        # Test non-existent tool
        non_existent = self.manager.get_tool("non_existent")
        assert non_existent is None
    
    def test_list_tools(self):
        """Test listing all available tools."""
        tools = self.manager.list_tools()
        assert isinstance(tools, dict)
        assert "calculator" in tools
        assert isinstance(tools["calculator"], str)
    
    def test_execute_tool_invalid_name(self):
        """Test executing tool with invalid name."""
        with pytest.raises(ValueError, match="Tool 'invalid' not found"):
            self.manager.execute_tool("invalid", expression="2+3")
    
    @patch('chatbot.tools.CalculatorTool.run')
    def test_execute_tool_success(self, mock_run):
        """Test successful tool execution."""
        mock_run.return_value = "The result of 2+3 is 5"
        
        result = self.manager.execute_tool("calculator", expression="2+3")
        
        assert "result of 2+3 is 5" in result
        mock_run.assert_called_once_with("2+3")
    
    @patch('chatbot.tools.CalculatorTool.run')
    def test_execute_tool_error(self, mock_run):
        """Test tool execution error handling."""
        mock_run.side_effect = Exception("Tool error")
        
        result = self.manager.execute_tool("calculator", expression="2+3")
        
        assert "error executing calculator" in result.lower()


class TestPlannerToolIntegration:
    """Test suite for planner integration with tools."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.planner = PlannerBot(enable_tools=True)
    
    def test_planner_with_tools_enabled(self):
        """Test that planner initializes with tools enabled."""
        assert self.planner.enable_tools is True
        assert self.planner.tool_manager is not None
    
    def test_planner_without_tools(self):
        """Test that planner works without tools enabled."""
        planner = PlannerBot(enable_tools=False)
        assert planner.enable_tools is False
        assert planner.tool_manager is None
    
    @patch('chatbot.tools.ToolManager.execute_tool')
    def test_calculation_with_tools(self, mock_execute):
        """Test calculation execution with tools enabled."""
        mock_execute.return_value = "The result of 5+3 is 8"
        
        result = self.planner.execute_conversation_turn("What's 5 + 3?")
        
        assert result["decision"].action.value == "calculate"
        assert "result of 5+3 is 8" in result["response"].lower()
        mock_execute.assert_called_once_with('calculator', expression='5 + 3')
    
    def test_calculation_without_tools(self):
        """Test calculation behavior without tools enabled."""
        planner = PlannerBot(enable_tools=False)
        
        result = planner.execute_conversation_turn("What's 5 + 3?")
        
        assert result["decision"].action.value == "calculate"
        assert "calculator tool will be integrated" in result["response"].lower()


class TestEndToEndIntegration:
    """End-to-end integration tests for Phase 3."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.planner = PlannerBot(enable_tools=True)
    
    @patch('httpx.Client.get')
    def test_complete_calculation_flow(self, mock_get):
        """Test complete flow from user input to calculation result."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 14}
        mock_get.return_value = mock_response
        
        # Test the complete flow
        result = self.planner.execute_conversation_turn("What's 2 + 3 * 4?")
        
        # Verify decision
        assert result["decision"].action.value == "calculate"
        assert result["decision"].parameters["expression"] == "2 + 3 * 4"
        
        # Verify response
        assert "result" in result["response"].lower()
        
        # Verify API was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "calculator" in call_args[0][0]
        assert call_args[1]["params"]["expr"] == "2 + 3 * 4"
    
    @patch('httpx.Client.get')
    def test_error_handling_flow(self, mock_get):
        """Test error handling in complete flow."""
        # Mock API error
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        result = self.planner.execute_conversation_turn("What's 10 / 0?")
        
        # Should still make a decision but handle the error gracefully
        assert result["decision"].action.value == "calculate"
        assert "unavailable" in result["response"].lower() or "error" in result["response"].lower()
    
    def test_conversation_memory_with_calculations(self):
        """Test that calculations are properly stored in memory."""
        # Mock successful calculation
        with patch('httpx.Client.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": 8}
            mock_get.return_value = mock_response
            
            result = self.planner.execute_conversation_turn("What's 5 + 3?")
            
            # Check that the conversation is in memory
            memory = result["memory_state"]
            assert "5 + 3" in memory
            
            # Follow up should have context
            result2 = self.planner.execute_conversation_turn("What about 10 - 2?")
            memory2 = result2["memory_state"]
            assert "5 + 3" in memory2  # Previous calculation still in memory
            assert "10 - 2" in memory2  # New calculation added


# Test runner for Phase 3
def run_phase3_tests():
    """
    Run all Phase 3 tests and display results.
    
    This function can be called to validate Phase 3 implementation
    before proceeding to Phase 4.
    """
    print("🧪 Running Phase 3 Test Suite...")
    print("=" * 50)
    
    # Run tests with pytest
    test_result = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if test_result == 0:
        print("\n✅ All Phase 3 tests passed!")
        print("🚀 Ready to proceed to Phase 4!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        print("🔧 Fix issues before proceeding to Phase 4.")
    
    return test_result == 0


if __name__ == "__main__":
    run_phase3_tests() 