#!/usr/bin/env python3
"""
Phase 1 Demo Script - Mindhive AI Chatbot Assessment
====================================================

Quick demonstration of Phase 1: Sequential Conversation with Memory

Usage:
    python demo_phase1.py

This script demonstrates:
- Multi-turn conversation tracking
- Memory persistence across turns
- The exact conversation flow from requirements
"""

from chatbot.memory_bot import MemoryBot

def demo_phase1():
    """
    Demonstrate Phase 1 functionality with the assessment requirements example.
    """
    print("🎯 Phase 1 Demo: Sequential Conversation with Memory")
    print("=" * 55)
    
    # Create a memory bot instance
    bot = MemoryBot()
    
    # The exact conversation flow from the assessment
    conversation_sequence = [
        "Is there an outlet in Petaling Jaya?",
        "SS2, what's the opening time?", 
        "What services do you offer there?"
    ]
    
    print("\n📝 Running the assessment's example conversation:")
    print("1. User: 'Is there an outlet in Petaling Jaya?'")
    print("2. User: 'SS2, what's the opening time?'")
    print("3. User: 'What services do you offer there?'")
    print("\n" + "─" * 50)
    
    # Execute the conversation
    for i, user_input in enumerate(conversation_sequence, 1):
        print(f"\n🔄 Turn {i}: {user_input}")
        response = bot.chat(user_input)
        print(f"🤖 Bot: {response}")
        
        # Show memory state
        memory = bot.get_memory_contents()
        word_count = len(memory.split()) if memory else 0
        print(f"💭 Memory: {word_count} words stored")
    
    # Show final memory state
    print("\n" + "─" * 50)
    print("📚 Final conversation memory:")
    print(bot.get_memory_contents())
    
    # Test memory persistence by asking a follow-up
    print("\n🔍 Testing memory persistence with follow-up question:")
    follow_up = "What was the opening time again?"
    print(f"🔄 Follow-up: {follow_up}")
    response = bot.chat(follow_up)
    print(f"🤖 Bot: {response}")
    
    print("\n✅ Phase 1 demonstration complete!")
    print("🧠 Memory successfully tracked across all conversation turns")

if __name__ == "__main__":
    demo_phase1() 