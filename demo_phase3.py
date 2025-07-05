#!/usr/bin/env python3
"""
Phase 3 Demo: Calculator Tool Integration
=========================================

This demo showcases the complete Phase 3 implementation including:
- Calculator API service
- LangChain tool integration
- Planner with actual tool execution
- Error handling and graceful degradation

Run this demo to see Phase 3 in action!
"""

import sys
import os
import time
import asyncio
from threading import Thread
import subprocess

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from chatbot.planner import PlannerBot
from chatbot.tools import ToolManager, calculate_expression
from app.calculator import CalculatorService
import uvicorn


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔧 {title}")
    print("-" * 40)


def start_api_server():
    """Start the FastAPI server in a background thread."""
    def run_server():
        try:
            uvicorn.run(
                "app.main:app",
                host="127.0.0.1",
                port=8000,
                log_level="warning",  # Reduce noise
                access_log=False
            )
        except Exception as e:
            print(f"API server error: {e}")
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give the server time to start
    print("🌐 Starting FastAPI server...")
    time.sleep(3)
    print("✅ API server running on http://localhost:8000")
    
    return server_thread


def test_calculator_service():
    """Test the core calculator service."""
    print_section("Calculator Service Test")
    
    calc = CalculatorService()
    
    test_cases = [
        ("2 + 3", "Basic addition"),
        ("10 * 5", "Multiplication"),
        ("15 / 3", "Division"),
        ("2 ** 3", "Exponentiation"),
        ("(2 + 3) * 4", "Order of operations"),
        ("2 + 3 * 4", "Precedence"),
        ("sqrt(16)", "Square root (if supported)"),
    ]
    
    for expression, description in test_cases:
        try:
            result = calc.evaluate_expression(expression)
            print(f"   ✅ {expression} = {result} ({description})")
        except Exception as e:
            print(f"   ❌ {expression} → Error: {e}")


def test_tool_integration():
    """Test the LangChain tool integration."""
    print_section("Tool Integration Test")
    
    # Test direct tool usage
    print("📋 Direct tool usage:")
    test_expressions = ["5 + 3", "10 * 2", "20 / 4"]
    
    for expr in test_expressions:
        try:
            result = calculate_expression(expr)
            print(f"   ✅ {expr} → {result}")
        except Exception as e:
            print(f"   ❌ {expr} → Error: {e}")
    
    # Test tool manager
    print("\n🔧 Tool Manager:")
    manager = ToolManager()
    tools = manager.list_tools()
    for name, description in tools.items():
        print(f"   📦 {name}: {description}")


def test_planner_integration():
    """Test the planner with tool integration."""
    print_section("Planner Integration Test")
    
    # Test with tools enabled
    print("🧠 Planner with tools enabled:")
    planner = PlannerBot(enable_tools=True)
    
    calculation_queries = [
        "What's 7 + 5?",
        "Calculate 15 * 3",
        "What is 100 / 4?",
        "Can you compute 2 to the power of 5?",
    ]
    
    for query in calculation_queries:
        try:
            print(f"\n👤 User: {query}")
            result = planner.execute_conversation_turn(query)
            
            print(f"🎯 Decision: {result['decision'].action.value}")
            print(f"🤖 Response: {result['response']}")
            
            # Show decision details
            if result['decision'].parameters:
                print(f"📊 Parameters: {result['decision'].parameters}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


def test_error_handling():
    """Test error handling capabilities."""
    print_section("Error Handling Test")
    
    planner = PlannerBot(enable_tools=True)
    
    error_cases = [
        ("What's 10 / 0?", "Division by zero"),
        ("Calculate abc + 5", "Invalid expression"),
        ("What is 2 + + 3?", "Syntax error"),
    ]
    
    for query, description in error_cases:
        try:
            print(f"\n👤 User: {query} ({description})")
            result = planner.execute_conversation_turn(query)
            print(f"🤖 Response: {result['response']}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def test_conversation_flow():
    """Test a complete conversation flow with calculations."""
    print_section("Conversation Flow Test")
    
    planner = PlannerBot(enable_tools=True)
    
    conversation = [
        "Hi there!",
        "Can you help me with some math?",
        "What's 25 + 17?",
        "Now multiply that result by 2",
        "What about 100 - 58?",
        "Thanks for your help!",
    ]
    
    print("💬 Simulating conversation:")
    for i, message in enumerate(conversation, 1):
        try:
            print(f"\n{i}. 👤 User: {message}")
            result = planner.execute_conversation_turn(message)
            print(f"   🤖 Bot: {result['response']}")
            
            # Show decision for non-trivial responses
            if result['decision'].action.value != "ask":
                print(f"   🎯 Action: {result['decision'].action.value}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_api_endpoints():
    """Test the FastAPI endpoints directly."""
    print_section("API Endpoints Test")
    
    import httpx
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    try:
        response = httpx.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = httpx.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test calculator endpoint
    test_calculations = [
        ("2+3", 5),
        ("10*5", 50),
        ("15/3", 5.0),
        ("2**3", 8),
    ]
    
    print("\n🧮 Calculator endpoint tests:")
    for expr, expected in test_calculations:
        try:
            response = httpx.get(f"{base_url}/calculator", params={"expr": expr})
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                if result == expected:
                    print(f"   ✅ {expr} = {result}")
                else:
                    print(f"   ❌ {expr} = {result} (expected {expected})")
            else:
                print(f"   ❌ {expr} → HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {expr} → Error: {e}")
    
    # Test error cases
    print("\n🚨 Error handling tests:")
    error_cases = [
        ("10/0", "Division by zero"),
        ("invalid", "Invalid expression"),
        ("", "Empty expression"),
    ]
    
    for expr, description in error_cases:
        try:
            response = httpx.get(f"{base_url}/calculator", params={"expr": expr})
            if response.status_code == 400:
                print(f"   ✅ {description}: Properly handled")
            else:
                print(f"   ❌ {description}: Unexpected status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: Error {e}")


def interactive_demo():
    """Run an interactive demo where user can input calculations."""
    print_section("Interactive Demo")
    
    planner = PlannerBot(enable_tools=True)
    
    print("💬 Interactive Calculator Demo")
    print("Enter mathematical expressions or questions. Type 'quit' to exit.")
    print("Examples: 'What's 5 + 3?', 'Calculate 10 * 7', '15 / 3'")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 Bot: Goodbye! Thanks for using the calculator!")
                break
            
            if not user_input:
                continue
            
            result = planner.execute_conversation_turn(user_input)
            print(f"🤖 Bot: {result['response']}")
            
            # Show additional info for calculations
            if result['decision'].action.value == "calculate":
                expr = result['decision'].parameters.get('expression', '')
                print(f"📊 Calculated: {expr}")
            
        except KeyboardInterrupt:
            print("\n🤖 Bot: Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Run the complete Phase 3 demo."""
    print_header("Phase 3: Calculator Tool Integration Demo")
    
    print("🎯 This demo showcases:")
    print("   • Calculator service with safe expression evaluation")
    print("   • FastAPI endpoints for calculator functionality")
    print("   • LangChain tool integration")
    print("   • Planner with actual tool execution")
    print("   • Comprehensive error handling")
    print("   • End-to-end conversation flow")
    
    # Start API server
    server_thread = start_api_server()
    
    try:
        # Run all tests
        test_calculator_service()
        test_tool_integration()
        test_api_endpoints()
        test_planner_integration()
        test_error_handling()
        test_conversation_flow()
        
        print_header("Phase 3 Demo Complete!")
        print("✅ All components working correctly!")
        print("🚀 Calculator tool integration successful!")
        
        # Ask if user wants interactive demo
        print("\n🎮 Would you like to try the interactive demo? (y/n)")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes']:
            interactive_demo()
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("🔧 Please check the setup and try again.")
    
    finally:
        print("\n🏁 Demo finished. API server will continue running in background.")
        print("📖 Check http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    main() 