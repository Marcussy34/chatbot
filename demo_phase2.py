#!/usr/bin/env python3
"""
Phase 2 Demo Script - Agentic Planning
======================================

Demonstration of Phase 2: Agentic Planning with decision-making logic

Usage:
    python demo_phase2.py

This script demonstrates:
- Intent classification and action selection
- Context-aware decision making
- Planning logic for different conversation types
- Integration with Phase 1 memory system
"""

from chatbot.planner import PlannerBot, ActionType

def demo_intent_classification():
    """
    Demonstrate intent classification and action selection.
    """
    print("🎯 Phase 2 Demo: Intent Classification & Action Selection")
    print("=" * 60)
    
    planner = PlannerBot()
    
    # Test different types of inputs
    test_scenarios = [
        {
            "category": "Mathematical Queries",
            "inputs": [
                "What's 15 + 7?",
                "Calculate 8 * 9",
                "What is 100 / 4?"
            ]
        },
        {
            "category": "Product Searches", 
            "inputs": [
                "What tumblers do you have?",
                "Show me your drinkware",
                "I want to buy a coffee mug"
            ]
        },
        {
            "category": "Outlet Queries",
            "inputs": [
                "Is there an outlet in PJ?",
                "What time does SS2 open?",
                "Where is the Damansara store?"
            ]
        },
        {
            "category": "Greetings & Endings",
            "inputs": [
                "Hello there!",
                "Thanks for your help",
                "Goodbye!"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['category']}:")
        print("─" * 40)
        
        for user_input in scenario["inputs"]:
            decision = planner.plan_next_action(user_input)
            
            print(f"\n💬 Input: '{user_input}'")
            print(f"🎯 Action: {decision.action.value.upper()}")
            print(f"💭 Reasoning: {decision.reasoning}")
            print(f"📊 Confidence: {decision.confidence:.1f}")
            
            if decision.parameters:
                print(f"📋 Parameters: {decision.parameters}")


def demo_conversation_flow():
    """
    Demonstrate how the planner handles a complete conversation flow.
    """
    print("\n\n🗣️  Phase 2 Demo: Complete Conversation Flow")
    print("=" * 50)
    
    planner = PlannerBot()
    
    # Simulate a realistic conversation about finding an outlet
    conversation_sequence = [
        "Hello",
        "Is there an outlet in Petaling Jaya?", 
        "SS2",
        "What time do you open?",
        "What services do you offer?",
        "Thanks, that's helpful!"
    ]
    
    print("📝 Simulating conversation about outlet inquiry:")
    print("   User wants to find an outlet, get hours, and learn about services")
    print("\n" + "─" * 50)
    
    for i, user_input in enumerate(conversation_sequence, 1):
        print(f"\n🔄 Turn {i}: '{user_input}'")
        
        # Get planning decision
        decision = planner.plan_next_action(user_input)
        
        print(f"🧠 Planner Decision:")
        print(f"   Action: {decision.action.value.upper()}")
        print(f"   Reasoning: {decision.reasoning}")
        print(f"   Confidence: {decision.confidence:.1f}")
        
        # Execute the conversation turn
        result = planner.execute_conversation_turn(user_input)
        
        print(f"🤖 Bot Response: {result['response']}")
        
        # Show memory growth
        memory_words = len(result['memory_state'].split()) if result['memory_state'] else 0
        print(f"💭 Memory: {memory_words} words stored")


def demo_context_awareness():
    """
    Demonstrate how context improves decision making.
    """
    print("\n\n🧠 Phase 2 Demo: Context-Aware Decision Making")
    print("=" * 55)
    
    planner = PlannerBot()
    
    print("📝 Demonstrating how context changes interpretation:")
    print("   Same input 'SS2' interpreted differently based on conversation history")
    print("\n" + "─" * 50)
    
    # Test 1: Ambiguous input without context
    print("\n🔍 Test 1: 'SS2' without any context")
    decision1 = planner.plan_next_action("SS2")
    print(f"   Action: {decision1.action.value.upper()}")
    print(f"   Reasoning: {decision1.reasoning}")
    
    # Test 2: Same input after outlet context
    print("\n🔍 Test 2: Building outlet context first...")
    planner.execute_conversation_turn("Is there an outlet in Petaling Jaya?")
    print("   Context added: User asked about outlets in PJ")
    
    print("\n🔍 Test 3: 'SS2' with outlet context")
    decision2 = planner.plan_next_action("SS2")
    print(f"   Action: {decision2.action.value.upper()}")
    print(f"   Reasoning: {decision2.reasoning}")
    
    print("\n💡 Notice how the same input is interpreted differently!")
    print("   Without context: General ASK action")
    print("   With context: Outlet-specific SQL_QUERY or targeted ASK")


def demo_missing_information_handling():
    """
    Demonstrate how the planner handles incomplete information.
    """
    print("\n\n❓ Phase 2 Demo: Missing Information Handling")
    print("=" * 50)
    
    planner = PlannerBot()
    
    incomplete_scenarios = [
        {
            "input": "Calculate",
            "missing": "mathematical expression",
            "explanation": "User wants calculation but didn't provide expression"
        },
        {
            "input": "What time?",
            "missing": "location context",
            "explanation": "User asks about time but no location specified"
        },
        {
            "input": "Show me products",
            "missing": "product preferences",
            "explanation": "User wants products but could be more specific"
        },
        {
            "input": "Where is it?",
            "missing": "subject reference",
            "explanation": "User asks 'where' but 'it' is undefined"
        }
    ]
    
    print("📝 Testing how planner handles incomplete information:")
    print("\n" + "─" * 50)
    
    for scenario in incomplete_scenarios:
        print(f"\n💬 Input: '{scenario['input']}'")
        print(f"❓ Missing: {scenario['missing']}")
        print(f"📝 Explanation: {scenario['explanation']}")
        
        decision = planner.plan_next_action(scenario["input"])
        
        print(f"🎯 Planner Action: {decision.action.value.upper()}")
        print(f"💭 Reasoning: {decision.reasoning}")
        
        if decision.action == ActionType.ASK:
            print(f"🗣️  Follow-up Question: {decision.parameters.get('message', 'N/A')}")


def demo_planning_explanation():
    """
    Show the planner's decision-making process explanation.
    """
    print("\n\n📚 Phase 2 Demo: Planning Process Explanation")
    print("=" * 55)
    
    planner = PlannerBot()
    
    print("🧠 How the Planner Makes Decisions:")
    print(planner.get_planning_explanation())
    
    print("\n🔄 Decision Flow Example:")
    print("   1. User: 'What's 5 + 3?'")
    print("   2. Intent Classification: 'calculation' (confidence: 0.9)")
    print("   3. Information Extraction: expression = '5 + 3'")
    print("   4. Missing Info Check: None (expression found)")
    print("   5. Action Selection: CALCULATE")
    print("   6. Response: Ready to calculate 5 + 3")


def main():
    """
    Run all Phase 2 demonstrations.
    """
    print("🧠 Mindhive AI Chatbot - Phase 2: Agentic Planning Demos")
    print("=" * 65)
    
    demos = [
        ("Intent Classification", demo_intent_classification),
        ("Conversation Flow", demo_conversation_flow), 
        ("Context Awareness", demo_context_awareness),
        ("Missing Information", demo_missing_information_handling),
        ("Planning Process", demo_planning_explanation)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {demo_name} demo: {e}")
        
        print("\n" + "="*65)
    
    print("\n✅ Phase 2 Demonstration Complete!")
    print("🚀 The planner successfully:")
    print("   • Classifies user intent from natural language")
    print("   • Selects appropriate actions (ASK, CALCULATE, SEARCH, QUERY, END)")
    print("   • Uses conversation context for better decisions")
    print("   • Handles incomplete information gracefully")
    print("   • Integrates with Phase 1 memory system")
    print("\n🎯 Ready for Phase 3: Tool Integration!")


if __name__ == "__main__":
    main() 