"""
Test Suite for Phase 1: Sequential Conversation Memory
=====================================================

This test suite validates the memory-based chatbot functionality,
ensuring proper state tracking across multi-turn conversations.

Test Coverage:
- Happy path: Complete conversation flows
- Interrupted paths: Partial conversations and error recovery
- Memory persistence and retrieval
- Edge cases and error handling
"""

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from chatbot.memory_bot import MemoryBot, SimpleLLM


class TestMemoryBot:
    """Test suite for the MemoryBot class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.bot = MemoryBot()
    
    def test_initialization(self):
        """Test that the bot initializes correctly with empty memory."""
        assert self.bot.memory is not None
        assert self.bot.llm is not None
        assert self.bot.conversation is not None
        # Memory should be empty initially
        assert self.bot.get_memory_contents() == ""
    
    def test_single_turn_conversation(self):
        """Test single turn conversation and memory storage."""
        user_input = "Hello"
        response = self.bot.chat(user_input)
        
        # Should get a response
        assert response is not None
        assert len(response) > 0
        
        # Memory should contain the interaction
        memory_contents = self.bot.get_memory_contents()
        assert "Hello" in memory_contents or "hello" in memory_contents.lower()
    
    def test_multi_turn_conversation_memory_persistence(self):
        """Test that memory persists across multiple conversation turns."""
        # First turn
        response1 = self.bot.chat("Is there an outlet in Petaling Jaya?")
        memory_after_turn1 = self.bot.get_memory_contents()
        
        # Second turn
        response2 = self.bot.chat("SS2, what's the opening time?")
        memory_after_turn2 = self.bot.get_memory_contents()
        
        # Memory should contain both interactions
        assert len(memory_after_turn2) > len(memory_after_turn1)
        assert "Petaling Jaya" in memory_after_turn2 or "petaling jaya" in memory_after_turn2.lower()
        assert "SS2" in memory_after_turn2 or "ss2" in memory_after_turn2.lower()
    
    def test_example_conversation_flow(self):
        """Test the exact conversation flow from Phase 1 requirements."""
        conversation_steps = [
            ("Is there an outlet in Petaling Jaya?", "outlet"),
            ("SS2, what's the opening time?", "9:00AM"),
            ("What services do you offer there?", "service")
        ]
        
        responses = []
        for user_input, expected_keyword in conversation_steps:
            response = self.bot.chat(user_input)
            responses.append(response)
            
            # Each response should be non-empty
            assert response is not None
            assert len(response.strip()) > 0
        
        # Check that memory contains all parts of the conversation
        final_memory = self.bot.get_memory_contents()
        assert "Petaling Jaya" in final_memory or "petaling jaya" in final_memory.lower()
        assert "SS2" in final_memory or "ss2" in final_memory.lower()
    
    def test_memory_clear_functionality(self):
        """Test that memory can be cleared properly."""
        # Add some conversation history
        self.bot.chat("Hello, is there an outlet in PJ?")
        self.bot.chat("SS2 please")
        
        # Verify memory contains content
        memory_before_clear = self.bot.get_memory_contents()
        assert len(memory_before_clear) > 0
        
        # Clear memory
        self.bot.clear_memory()
        
        # Verify memory is empty
        memory_after_clear = self.bot.get_memory_contents()
        assert memory_after_clear == ""
    
    def test_error_handling_in_chat(self):
        """Test that the bot handles errors gracefully."""
        # Test with empty input
        response = self.bot.chat("")
        assert response is not None
        
        # Test with very long input
        long_input = "x" * 1000
        response = self.bot.chat(long_input)
        assert response is not None
        assert "error" not in response.lower() or "sorry" in response.lower()


class TestSimpleLLM:
    """Test suite for the SimpleLLM class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.llm = SimpleLLM()
    
    def test_llm_initialization(self):
        """Test that the LLM initializes with proper outlets database."""
        outlets_db = self.llm._get_outlets_db()
        assert outlets_db is not None
        assert "ss2" in outlets_db
        assert "pj" in outlets_db
    
    def test_outlet_location_recognition(self):
        """Test that LLM recognizes outlet location queries."""
        prompt = "Human: Is there an outlet in Petaling Jaya?"
        response = self.llm._call(prompt)
        
        assert "outlet" in response.lower()
        assert "petaling jaya" in response.lower() or "pj" in response.lower()
    
    def test_ss2_specific_queries(self):
        """Test responses to SS2-specific queries."""
        # Test opening time query
        prompt = "Human: SS2, what's the opening time?"
        response = self.llm._call(prompt)
        
        assert "9:00AM" in response or "9am" in response.lower()
        assert "SS2" in response or "ss2" in response.lower()
    
    def test_greeting_responses(self):
        """Test that the LLM responds appropriately to greetings."""
        greetings = ["Hello", "Hi", "Hey"]
        
        for greeting in greetings:
            prompt = f"Human: {greeting}"
            response = self.llm._call(prompt)
            
            assert response is not None
            assert len(response) > 0
            assert "hello" in response.lower() or "hi" in response.lower()
    
    def test_unknown_input_handling(self):
        """Test that LLM provides fallback responses for unknown inputs."""
        unknown_inputs = ["xyz123", "random gibberish", ""]
        
        for unknown_input in unknown_inputs:
            prompt = f"Human: {unknown_input}"
            response = self.llm._call(prompt)
            
            assert response is not None
            assert len(response) > 0
            # Should provide helpful fallback
            assert "help" in response.lower() or "outlet" in response.lower()


class TestInterruptedPaths:
    """Test suite for interrupted conversation paths and error recovery."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.bot = MemoryBot()
    
    def test_partial_conversation_recovery(self):
        """Test that bot can recover from incomplete conversations."""
        # Start a conversation but don't complete it
        response1 = self.bot.chat("Is there an outlet")  # Incomplete query
        assert response1 is not None
        
        # Continue with more context
        response2 = self.bot.chat("in Petaling Jaya?")
        assert response2 is not None
        
        # Should still be able to continue the conversation
        response3 = self.bot.chat("SS2")
        assert response3 is not None
    
    def test_context_switching(self):
        """Test that bot handles sudden context changes gracefully."""
        # Start with outlet inquiry
        self.bot.chat("Is there an outlet in PJ?")
        
        # Suddenly switch to greeting
        response = self.bot.chat("Hello")
        assert response is not None
        
        # Switch back to outlet context
        response = self.bot.chat("What about SS2?")
        assert response is not None
    
    def test_repeated_queries(self):
        """Test that bot handles repeated or similar queries properly."""
        query = "Is there an outlet in Petaling Jaya?"
        
        # Ask the same question multiple times
        response1 = self.bot.chat(query)
        response2 = self.bot.chat(query)
        response3 = self.bot.chat(query)
        
        # All responses should be valid
        assert all(r is not None and len(r) > 0 for r in [response1, response2, response3])
    
    def test_memory_overflow_protection(self):
        """Test that the system handles very long conversations."""
        # Simulate a very long conversation
        for i in range(50):
            response = self.bot.chat(f"Message number {i}")
            assert response is not None
        
        # Memory should still function
        memory_contents = self.bot.get_memory_contents()
        assert memory_contents is not None
    
    def test_special_characters_handling(self):
        """Test that bot handles special characters and Unicode."""
        special_inputs = [
            "Is there an outlet in PJ? 🏪",
            "SS2 café ☕",
            "What's the time? ⏰",
            "Test with symbols: @#$%^&*()"
        ]
        
        for special_input in special_inputs:
            response = self.bot.chat(special_input)
            assert response is not None
            assert len(response) > 0
    
    def test_empty_and_whitespace_inputs(self):
        """Test handling of empty and whitespace-only inputs."""
        empty_inputs = ["", "   ", "\n", "\t", "    \n    "]
        
        for empty_input in empty_inputs:
            response = self.bot.chat(empty_input)
            assert response is not None
            # Should provide some kind of helpful response, not crash


class TestMemoryIntegration:
    """Integration tests for memory functionality across the system."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.bot = MemoryBot()
    
    def test_memory_content_accuracy(self):
        """Test that memory accurately stores conversation content."""
        user_messages = [
            "Hello",
            "Is there an outlet in Petaling Jaya?",
            "SS2, what's the opening time?"
        ]
        
        for message in user_messages:
            self.bot.chat(message)
        
        memory_contents = self.bot.get_memory_contents()
        
        # All user messages should be in memory
        for message in user_messages:
            assert message in memory_contents or message.lower() in memory_contents.lower()
    
    def test_memory_retrieval_methods(self):
        """Test different ways to retrieve memory contents."""
        self.bot.chat("Test message for memory")
        
        # Test direct memory access
        memory_via_method = self.bot.get_memory_contents()
        memory_via_attribute = self.bot.memory.buffer
        
        assert memory_via_method == memory_via_attribute
        assert "Test message" in memory_via_method or "test message" in memory_via_method.lower()
    
    def test_memory_state_consistency(self):
        """Test that memory state remains consistent across operations."""
        # Initial state
        initial_memory = self.bot.get_memory_contents()
        assert initial_memory == ""
        
        # Add conversation
        self.bot.chat("First message")
        memory_after_first = self.bot.get_memory_contents()
        assert len(memory_after_first) > len(initial_memory)
        
        # Add more conversation
        self.bot.chat("Second message")
        memory_after_second = self.bot.get_memory_contents()
        assert len(memory_after_second) > len(memory_after_first)
        
        # Memory should be cumulative
        assert "First message" in memory_after_second or "first message" in memory_after_second.lower()
        assert "Second message" in memory_after_second or "second message" in memory_after_second.lower()


# Test runner for Phase 1
def run_phase1_tests():
    """
    Run all Phase 1 tests and display results.
    
    This function can be called to validate Phase 1 implementation
    before proceeding to Phase 2.
    """
    print("🧪 Running Phase 1 Test Suite...")
    print("=" * 50)
    
    # Run tests with pytest
    test_result = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if test_result == 0:
        print("\n✅ All Phase 1 tests passed!")
        print("🚀 Ready to proceed to Phase 2!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        print("🔧 Fix issues before proceeding to Phase 2.")
    
    return test_result == 0


if __name__ == "__main__":
    run_phase1_tests() 