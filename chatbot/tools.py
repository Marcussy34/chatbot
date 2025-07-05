"""
Tool Integration - Phase 3+ Tool Calling
========================================

LangChain tool wrappers for calculator API and future integrations.

This module provides:
- Calculator tool for mathematical expressions
- HTTP client for API communication
- Error handling and graceful degradation
- Tool integration with the planner system
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, Union
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)


class CalculatorInput(BaseModel):
    """Input schema for calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2+3', '10*5')")


class CalculatorTool(BaseTool):
    """
    LangChain tool for calculator API integration.
    
    This tool provides safe mathematical expression evaluation through
    the FastAPI calculator service with comprehensive error handling.
    """
    
    name: str = "calculator"
    description: str = """
    Evaluate mathematical expressions safely. 
    Supports basic arithmetic (+, -, *, /, %, **), parentheses, and order of operations.
    Examples: '2+3', '10*5', '(2+3)*4', '15/3', '2**3'
    """
    args_schema: type = CalculatorInput
    return_direct: bool = False
    
    # Custom fields for this tool
    base_url: str = "http://localhost:8000"
    timeout: float = 5.0
    client: Optional[httpx.Client] = None
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 5.0, **kwargs):
        """
        Initialize calculator tool.
        
        Args:
            base_url: Base URL of the FastAPI service
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, timeout=timeout, **kwargs)
        # Initialize after super().__init__
        object.__setattr__(self, 'client', httpx.Client(timeout=self.timeout))
    
    def _run(self, expression: str) -> str:
        """
        Execute calculator tool synchronously.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            String containing the result or error message
        """
        try:
            logger.info(f"Calculator tool called with expression: '{expression}'")
            
            # Make API request
            base_url = self.base_url.rstrip('/')
            response = self.client.get(
                f"{base_url}/calculator",
                params={"expr": expression}
            )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                logger.info(f"Calculator result: {result}")
                return f"The result of {expression} is {result}"
            
            else:
                # Handle API errors gracefully
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                logger.warning(f"Calculator API error: {error_msg}")
                return f"Error calculating {expression}: {error_msg}"
        
        except httpx.ConnectError:
            logger.error("Calculator API connection failed")
            return f"Calculator service is currently unavailable. Cannot evaluate: {expression}"
        
        except httpx.TimeoutException:
            logger.error("Calculator API timeout")
            return f"Calculator service timed out. Cannot evaluate: {expression}"
        
        except Exception as e:
            logger.error(f"Unexpected error in calculator tool: {e}")
            return f"Unexpected error while calculating {expression}: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """
        Execute calculator tool asynchronously.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            String containing the result or error message
        """
        try:
            logger.info(f"Calculator tool (async) called with expression: '{expression}'")
            
            base_url = self.base_url.rstrip('/')
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{base_url}/calculator",
                    params={"expr": expression}
                )
                
                # Handle response
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result")
                    logger.info(f"Calculator result: {result}")
                    return f"The result of {expression} is {result}"
                
                else:
                    # Handle API errors gracefully
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                    logger.warning(f"Calculator API error: {error_msg}")
                    return f"Error calculating {expression}: {error_msg}"
        
        except httpx.ConnectError:
            logger.error("Calculator API connection failed")
            return f"Calculator service is currently unavailable. Cannot evaluate: {expression}"
        
        except httpx.TimeoutException:
            logger.error("Calculator API timeout")
            return f"Calculator service timed out. Cannot evaluate: {expression}"
        
        except Exception as e:
            logger.error(f"Unexpected error in calculator tool: {e}")
            return f"Unexpected error while calculating {expression}: {str(e)}"


class ToolManager:
    """
    Manager for all available tools in the chatbot system.
    
    This class provides a centralized way to manage and access
    all tools available to the planner and agent.
    """
    
    def __init__(self, calculator_base_url: str = "http://localhost:8000"):
        """
        Initialize tool manager.
        
        Args:
            calculator_base_url: Base URL for calculator API
        """
        self.calculator_base_url = calculator_base_url
        self._tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools."""
        # Calculator tool
        self._tools["calculator"] = CalculatorTool(base_url=self.calculator_base_url)
        
        logger.info(f"Tool manager initialized with {len(self._tools)} tools")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a specific tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """
        Get all available tools.
        
        Returns:
            Dictionary mapping tool names to tool instances
        """
        return self._tools.copy()
    
    def list_tools(self) -> Dict[str, str]:
        """
        Get a list of all available tools with descriptions.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            name: tool.description.strip()
            for name, tool in self._tools.items()
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool is not found
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            available_tools = ", ".join(self._tools.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        
        try:
            # Pass parameters directly if it's a single parameter
            if len(kwargs) == 1 and 'expression' in kwargs:
                return tool.run(kwargs['expression'])
            else:
                return tool.run(kwargs)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    def test_tool_connectivity(self) -> Dict[str, bool]:
        """
        Test connectivity to all external tools/APIs.
        
        Returns:
            Dictionary mapping tool names to connectivity status
        """
        results = {}
        
        # Test calculator tool
        try:
            calculator = self.get_tool("calculator")
            test_result = calculator.run("2+2")
            results["calculator"] = "result" in test_result.lower()
        except Exception as e:
            logger.warning(f"Calculator connectivity test failed: {e}")
            results["calculator"] = False
        
        return results


# Convenience functions for direct tool usage
def calculate_expression(expression: str, base_url: str = "http://localhost:8000") -> str:
    """
    Convenience function for direct calculator usage.
    
    Args:
        expression: Mathematical expression to evaluate
        base_url: Calculator API base URL
        
    Returns:
        Calculation result or error message
    """
    calculator = CalculatorTool(base_url=base_url)
    return calculator.run(expression)


def create_tool_manager(calculator_url: str = "http://localhost:8000") -> ToolManager:
    """
    Create and configure a tool manager instance.
    
    Args:
        calculator_url: Calculator API base URL
        
    Returns:
        Configured ToolManager instance
    """
    return ToolManager(calculator_base_url=calculator_url)


# Example usage and testing
if __name__ == "__main__":
    # Test tool integration
    print("🔧 Tool Integration Test")
    print("=" * 30)
    
    # Create tool manager
    manager = ToolManager()
    
    # List available tools
    print("\n📋 Available Tools:")
    for name, description in manager.list_tools().items():
        print(f"   {name}: {description}")
    
    # Test calculator tool
    print("\n🧮 Calculator Tool Test:")
    test_expressions = ["2+3", "10*5", "15/3", "2**3"]
    
    for expr in test_expressions:
        try:
            result = calculate_expression(expr)
            print(f"   ✅ {expr} → {result}")
        except Exception as e:
            print(f"   ❌ {expr} → Error: {e}")
    
    # Test connectivity
    print("\n🔗 Connectivity Test:")
    connectivity = manager.test_tool_connectivity()
    for tool, status in connectivity.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {tool}: {'Connected' if status else 'Disconnected'}") 