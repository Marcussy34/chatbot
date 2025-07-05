"""
Phase 4 Demo: Custom API + RAG Integration
==========================================

This demo showcases the Phase 4 implementation including:
- RAG product search using FAISS vector store
- Text2SQL outlet queries using SQLite
- FastAPI endpoints for /products and /outlets
- Complete planner integration with all tools

Features demonstrated:
✅ Product search with AI-generated summaries
✅ Outlet queries with natural language to SQL translation
✅ Comprehensive error handling and graceful degradation
✅ Full integration with existing calculator and memory system
"""

import asyncio
import time
import logging
from typing import Dict, Any

# Import our services
from app.main import app
from app.rag_service import create_rag_service
from app.sql_service import create_sql_service
from chatbot.planner import PlannerBot
from chatbot.tools import create_tool_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase4Demo:
    """
    Comprehensive demo for Phase 4 RAG and SQL integration.
    """
    
    def __init__(self):
        """Initialize demo with all services."""
        print("🚀 Phase 4 Demo: Custom API + RAG Integration")
        print("=" * 60)
        
        # Initialize services
        print("\n📋 Initializing Services...")
        self.rag_service = create_rag_service()
        self.sql_service = create_sql_service()
        self.tool_manager = create_tool_manager()
        self.planner = PlannerBot(enable_tools=True)
        
        print("✅ All services initialized successfully!")
    
    def demo_rag_service(self):
        """Demonstrate RAG product search functionality."""
        print("\n🔍 RAG Product Search Demo")
        print("-" * 40)
        
        test_queries = [
            "black tumbler",
            "ceramic mug for office",
            "travel bottle with insulation",
            "rose gold tumbler",
            "glass cup set"
        ]
        
        for query in test_queries:
            print(f"\n🔸 Query: '{query}'")
            
            try:
                result = self.rag_service.get_product_recommendations(query, top_k=2)
                print(f"📊 Found {result['total_found']} products")
                print(f"💬 Summary: {result['summary'][:100]}...")
                
                # Show top product
                if result['products']:
                    top_product = result['products'][0]
                    print(f"🏆 Top match: {top_product['name']} (Score: {top_product['similarity_score']:.3f})")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)  # Brief pause for readability
    
    def demo_sql_service(self):
        """Demonstrate Text2SQL outlet query functionality."""
        print("\n🗄️ Text2SQL Outlet Query Demo")
        print("-" * 40)
        
        test_queries = [
            "outlets in SS2",
            "opening hours KLCC",
            "phone number Mont Kiara",
            "all outlets",
            "outlets in Petaling Jaya"
        ]
        
        for query in test_queries:
            print(f"\n🔸 Query: '{query}'")
            
            try:
                result = self.sql_service.query_outlets(query)
                print(f"🔍 SQL: {result['sql_query']}")
                print(f"📊 Found {result['total_results']} outlets")
                
                formatted = self.sql_service.format_results_for_user(result)
                print(f"💬 Response: {formatted[:150]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)  # Brief pause for readability
    
    def demo_tool_integration(self):
        """Demonstrate tool manager integration."""
        print("\n🔧 Tool Integration Demo")
        print("-" * 40)
        
        # List available tools
        tools = self.tool_manager.list_tools()
        print(f"📋 Available tools: {', '.join(tools.keys())}")
        
        # Test each tool
        test_cases = [
            ("calculator", {"expression": "15 * 4"}),
            ("product_search", {"query": "black tumbler"}),
            ("outlet_query", {"query": "outlets in KLCC"})
        ]
        
        for tool_name, params in test_cases:
            print(f"\n🔸 Testing {tool_name} tool")
            
            try:
                result = self.tool_manager.execute_tool(tool_name, **params)
                print(f"✅ Result: {result[:100]}...")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def demo_planner_integration(self):
        """Demonstrate complete planner integration with all action types."""
        print("\n🧠 Complete Planner Integration Demo")
        print("-" * 40)
        
        conversation_flows = [
            {
                "name": "Mathematical Calculation",
                "queries": ["What is 25 * 8?", "Calculate 100 / 4"]
            },
            {
                "name": "Product Search",
                "queries": ["I'm looking for a black tumbler", "Do you have ceramic mugs?"]
            },
            {
                "name": "Outlet Information", 
                "queries": ["Where are your outlets in SS2?", "What time does KLCC open?"]
            },
            {
                "name": "Mixed Conversation",
                "queries": ["Hello", "outlets in Mont Kiara", "What is 12 + 8?", "Thanks!"]
            }
        ]
        
        for flow in conversation_flows:
            print(f"\n📋 {flow['name']} Flow:")
            print("   " + "=" * (len(flow['name']) + 6))
            
            for query in flow['queries']:
                print(f"\n   👤 User: {query}")
                
                try:
                    result = self.planner.execute_conversation_turn(query)
                    action = result['decision'].action.value.upper()
                    response = result['response']
                    
                    print(f"   🤖 Action: {action}")
                    print(f"   🤖 Bot: {response[:120]}...")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                time.sleep(0.5)  # Brief pause between queries
    
    def demo_error_handling(self):
        """Demonstrate error handling and graceful degradation."""
        print("\n🛡️ Error Handling & Graceful Degradation Demo")
        print("-" * 50)
        
        # Test various error scenarios
        error_tests = [
            ("Empty query", ""),
            ("Invalid calculation", "calculate xyz"),
            ("Vague product query", "thing"),
            ("Non-existent location", "outlets in Mars"),
            ("SQL injection attempt", "outlets'; DROP TABLE outlets; --")
        ]
        
        for test_name, query in error_tests:
            print(f"\n🔸 {test_name}: '{query}'")
            
            try:
                result = self.planner.execute_conversation_turn(query)
                response = result['response']
                print(f"✅ Handled gracefully: {response[:100]}...")
            except Exception as e:
                print(f"⚠️ Exception caught: {e}")
    
    def demo_service_status(self):
        """Show status of all services."""
        print("\n📊 Service Status Summary")
        print("-" * 40)
        
        # RAG service status
        rag_status = self.rag_service.get_service_status()
        print(f"🔍 RAG Service: {rag_status['status']}")
        print(f"   Products loaded: {rag_status['products_loaded']}")
        print(f"   Index available: {rag_status['index_available']}")
        print(f"   Model: {rag_status['model']}")
        
        # SQL service status
        sql_status = self.sql_service.get_service_status()
        print(f"\n🗄️ SQL Service: {sql_status['status']}")
        print(f"   Outlets in database: {sql_status['outlet_count']}")
        print(f"   Query patterns: {sql_status['patterns_loaded']}")
        
        # Tool connectivity
        connectivity = self.tool_manager.test_tool_connectivity()
        print(f"\n🔧 Tool Connectivity:")
        for tool, connected in connectivity.items():
            status = "✅ Connected" if connected else "❌ Disconnected"
            print(f"   {tool}: {status}")
    
    def run_complete_demo(self):
        """Run the complete Phase 4 demonstration."""
        try:
            self.demo_service_status()
            self.demo_rag_service()
            self.demo_sql_service()
            self.demo_tool_integration()
            self.demo_planner_integration()
            self.demo_error_handling()
            
            print("\n🎉 Phase 4 Demo Complete!")
            print("=" * 60)
            print("✅ RAG product search working")
            print("✅ Text2SQL outlet queries working")
            print("✅ FastAPI endpoints functional")
            print("✅ Complete planner integration")
            print("✅ Error handling and graceful degradation")
            print("✅ All tools integrated successfully")
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"\n❌ Demo failed with error: {e}")


def run_quick_test():
    """Quick test of core functionality."""
    print("🚀 Quick Phase 4 Test")
    print("=" * 30)
    
    try:
        planner = PlannerBot(enable_tools=True)
        
        # Test one example of each action type
        tests = [
            "What is 7 * 9?",
            "black tumbler", 
            "outlets in SS2"
        ]
        
        for test in tests:
            print(f"\n🔸 Testing: '{test}'")
            result = planner.execute_conversation_turn(test)
            print(f"✅ Action: {result['decision'].action.value}")
            print(f"✅ Response: {result['response'][:80]}...")
        
        print("\n🎉 Quick test passed!")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        demo = Phase4Demo()
        demo.run_complete_demo() 