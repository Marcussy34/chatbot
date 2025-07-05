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


class ProductSearchInput(BaseModel):
    """Input schema for product search tool."""
    query: str = Field(description="Search query for drinkware products (e.g., 'black tumbler', 'ceramic mug')")


class OutletQueryInput(BaseModel):
    """Input schema for outlet query tool."""
    query: str = Field(description="Natural language query about outlets (e.g., 'outlets in SS2', 'opening hours KLCC')")


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


class ProductSearchTool(BaseTool):
    """
    LangChain tool for product search using RAG.
    
    This tool provides semantic search over ZUS Coffee drinkware products
    with AI-generated summaries.
    """
    
    name: str = "product_search"
    description: str = """
    Search for ZUS Coffee drinkware products using natural language.
    Returns AI-generated summaries of relevant products with details.
    Examples: 'black tumbler', 'ceramic mug for office', 'travel bottle'
    """
    args_schema: type = ProductSearchInput
    return_direct: bool = False
    
    # Custom fields for this tool
    base_url: str = "http://localhost:8000"
    timeout: float = 10.0
    client: Optional[httpx.Client] = None
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 10.0, **kwargs):
        """
        Initialize product search tool.
        
        Args:
            base_url: Base URL of the FastAPI service
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, timeout=timeout, **kwargs)
        object.__setattr__(self, 'client', httpx.Client(timeout=self.timeout))
    
    def _run(self, query: str) -> str:
        """
        Execute product search tool synchronously.
        
        Args:
            query: Search query for products
            
        Returns:
            String containing the search results summary
        """
        try:
            logger.info(f"Product search tool called with query: '{query}'")
            
            # Make API request
            base_url = self.base_url.rstrip('/')
            response = self.client.get(
                f"{base_url}/products",
                params={"query": query}
            )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "No summary available")
                logger.info(f"Product search successful: {data.get('total_found', 0)} products found")
                return summary
            
            else:
                # Handle API errors gracefully
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                logger.warning(f"Product search API error: {error_msg}")
                return f"Error searching for products '{query}': {error_msg}"
        
        except httpx.ConnectError:
            logger.error("Product search API connection failed")
            return f"Product search service is currently unavailable. Cannot search for: {query}"
        
        except httpx.TimeoutException:
            logger.error("Product search API timeout")
            return f"Product search service timed out. Cannot search for: {query}"
        
        except Exception as e:
            logger.error(f"Unexpected error in product search tool: {e}")
            return f"Unexpected error while searching for products '{query}': {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Execute product search tool asynchronously."""
        # For simplicity, use sync version
        return self._run(query)


class OutletQueryTool(BaseTool):
    """
    LangChain tool for outlet queries using Text2SQL.
    
    This tool translates natural language queries to SQL and returns
    formatted outlet information.
    """
    
    name: str = "outlet_query"
    description: str = """
    Query ZUS Coffee outlet information using natural language.
    Returns formatted outlet details including location, hours, and contact info.
    Examples: 'outlets in Petaling Jaya', 'opening hours SS2', 'phone number KLCC'
    """
    args_schema: type = OutletQueryInput
    return_direct: bool = False
    
    # Custom fields for this tool
    base_url: str = "http://localhost:8000"
    timeout: float = 10.0
    client: Optional[httpx.Client] = None
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 10.0, **kwargs):
        """
        Initialize outlet query tool.
        
        Args:
            base_url: Base URL of the FastAPI service
            timeout: Request timeout in seconds
        """
        super().__init__(base_url=base_url, timeout=timeout, **kwargs)
        object.__setattr__(self, 'client', httpx.Client(timeout=self.timeout))
    
    def _run(self, query: str) -> str:
        """
        Execute outlet query tool synchronously.
        
        Args:
            query: Natural language query about outlets
            
        Returns:
            String containing the formatted outlet information
        """
        try:
            logger.info(f"Outlet query tool called with query: '{query}'")
            
            # Make API request
            base_url = self.base_url.rstrip('/')
            response = self.client.get(
                f"{base_url}/outlets",
                params={"query": query}
            )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                formatted_response = data.get("formatted_response", "No information available")
                logger.info(f"Outlet query successful: {data.get('total_results', 0)} outlets found")
                return formatted_response
            
            else:
                # Handle API errors gracefully
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                logger.warning(f"Outlet query API error: {error_msg}")
                return f"Error querying outlets '{query}': {error_msg}"
        
        except httpx.ConnectError:
            logger.error("Outlet query API connection failed")
            return f"Outlet query service is currently unavailable. Cannot process: {query}"
        
        except httpx.TimeoutException:
            logger.error("Outlet query API timeout")
            return f"Outlet query service timed out. Cannot process: {query}"
        
        except Exception as e:
            logger.error(f"Unexpected error in outlet query tool: {e}")
            return f"Unexpected error while querying outlets '{query}': {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Execute outlet query tool asynchronously."""
        # For simplicity, use sync version
        return self._run(query)


class ToolManager:
    """
    Manager for all available tools in the chatbot system.
    
    This class provides a centralized way to manage and access
    all tools available to the planner and agent.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize tool manager.
        
        Args:
            base_url: Base URL for all API services
        """
        self.base_url = base_url
        self._tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools."""
        # Calculator tool
        self._tools["calculator"] = CalculatorTool(base_url=self.base_url)
        
        # Product search tool (RAG)
        self._tools["product_search"] = ProductSearchTool(base_url=self.base_url)
        
        # Outlet query tool (Text2SQL)
        self._tools["outlet_query"] = OutletQueryTool(base_url=self.base_url)
        
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


def create_tool_manager(base_url: str = "http://localhost:8000") -> ToolManager:
    """
    Create and configure a tool manager instance.
    
    Args:
        base_url: API base URL for all services
        
    Returns:
        Configured ToolManager instance
    """
    return ToolManager(base_url=base_url)


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