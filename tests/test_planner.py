"""
Test Suite for Phase 2: Agentic Planning
========================================

This test suite validates the planner functionality including intent classification,
action selection, and decision-making logic.

Test Coverage:
- Intent classification accuracy
- Action selection logic
- Information extraction
- Missing information detection
- Planning decision reasoning
- Integration with memory system
"""

import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from chatbot.planner import (
    PlannerBot, ActionType, PlannerDecision, 
    IntentClassifier, InformationExtractor
)


class TestIntentClassifier:
    """Test suite for the IntentClassifier class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.classifier = IntentClassifier()
    
    def test_mathematical_intent_classification(self):
        """Test classification of mathematical expressions."""
        math_inputs = [
            "What's 5 + 3?",
            "Calculate 10 * 2",
            "2 + 2",
            "solve 15 / 3",
            "compute 7 - 4"
        ]
        
        for math_input in math_inputs:
            intent, confidence = self.classifier.classify_intent(math_input)
            assert intent == "calculation"
            assert confidence >= 0.8
    
    def test_product_search_intent_classification(self):
        """Test classification of product search queries."""
        product_inputs = [
            "What products do you have?",
            "Show me your tumblers",
            "I want to buy a coffee mug",
            "What's the best ZUS bottle?",
            "Do you sell drinkware?"
        ]
        
        for product_input in product_inputs:
            intent, confidence = self.classifier.classify_intent(product_input)
            assert intent == "product_search"
            assert confidence >= 0.7
    
    def test_outlet_query_intent_classification(self):
        """Test classification of outlet/location queries."""
        outlet_inputs = [
            "Is there an outlet in PJ?",
            "Where is the SS2 store?",
            "What time does the outlet open?",
            "Show me outlets in Petaling Jaya",
            "How do I get to the Damansara branch?"
        ]
        
        for outlet_input in outlet_inputs:
            intent, confidence = self.classifier.classify_intent(outlet_input)
            assert intent == "outlet_query"
            assert confidence >= 0.7
    
    def test_greeting_intent_classification(self):
        """Test classification of greetings and conversation endings."""
        greeting_inputs = [
            "Hello",
            "Hi there",
            "Good morning",
            "Thanks",
            "Goodbye",
            "Bye"
        ]
        
        for greeting_input in greeting_inputs:
            intent, confidence = self.classifier.classify_intent(greeting_input)
            assert intent == "greeting"
            assert confidence >= 0.8
    
    def test_context_based_classification(self):
        """Test that context improves classification accuracy."""
        # Simulate conversation about outlets
        history = "Human: Is there an outlet in PJ?\nAI: Yes! Which outlet are you referring to?"
        
        # User provides location context
        intent, confidence = self.classifier.classify_intent("SS2", history)
        assert intent == "outlet_query"
        assert confidence >= 0.8
        
        # Simulate conversation about products
        product_history = "Human: What products do you have?\nAI: We have various drinkware items."
        intent, confidence = self.classifier.classify_intent("tumblers", product_history)
        assert intent == "product_search"
        assert confidence >= 0.7


class TestInformationExtractor:
    """Test suite for the InformationExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.extractor = InformationExtractor()
    
    def test_calculation_expression_extraction(self):
        """Test extraction of mathematical expressions."""
        test_cases = [
            ("What's 5 + 3?", "5 + 3"),
            ("Calculate 10 * 2", "10 * 2"),
            ("What is 15 / 3", "15 / 3"),
            ("2^3", "2^3"),
            ("7.5 - 2.1", "7.5 - 2.1")
        ]
        
        for input_text, expected in test_cases:
            result = self.extractor.extract_calculation_expression(input_text)
            assert result is not None
            # Normalize whitespace for comparison
            assert result.replace(" ", "") == expected.replace(" ", "")
    
    def test_location_info_extraction(self):
        """Test extraction of location information."""
        test_cases = [
            ("Is there an outlet in SS2?", {"location": "SS2"}),
            ("Show me stores in Petaling Jaya", {"area": "Petaling Jaya"}),
            ("What time does SS2 open?", {"location": "SS2", "query_type": "hours"}),
            ("Where is the PJ outlet?", {"area": "Petaling Jaya", "query_type": "location"}),
            ("What services are available at KL?", {"area": "Kuala Lumpur", "query_type": "services"})
        ]
        
        for input_text, expected in test_cases:
            result = self.extractor.extract_location_info(input_text)
            for key, value in expected.items():
                assert result.get(key) == value
    
    def test_missing_info_identification(self):
        """Test identification of missing information."""
        # Test outlet query with missing location
        missing = self.extractor.identify_missing_info(
            "outlet_query", {}, "Human: What time do you open?"
        )
        assert "location" in missing
        
        # Test outlet query with missing query type
        missing = self.extractor.identify_missing_info(
            "outlet_query", {"location": "SS2"}, ""
        )
        assert "query_type" in missing
        
        # Test calculation with missing expression
        missing = self.extractor.identify_missing_info(
            "calculation", {"text": "calculate something"}, ""
        )
        assert "mathematical_expression" in missing


class TestPlannerBot:
    """Test suite for the main PlannerBot class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.planner = PlannerBot()
    
    def test_planner_initialization(self):
        """Test that planner initializes correctly."""
        assert self.planner.memory_bot is not None
        assert self.planner.intent_classifier is not None
        assert self.planner.info_extractor is not None
    
    def test_calculation_planning(self):
        """Test planning for mathematical calculations."""
        decision = self.planner.plan_next_action("What's 5 + 3?")
        
        assert decision.action == ActionType.CALCULATE
        assert "5 + 3" in decision.parameters.get("expression", "")
        assert decision.confidence >= 0.8
        assert "mathematical expression" in decision.reasoning.lower()
    
    def test_product_search_planning(self):
        """Test planning for product searches."""
        decision = self.planner.plan_next_action("What tumblers do you have?")
        
        assert decision.action == ActionType.RAG_SEARCH
        assert "tumblers" in decision.parameters.get("query", "").lower()
        assert decision.confidence >= 0.7
        assert "product" in decision.reasoning.lower()
    
    def test_outlet_query_planning(self):
        """Test planning for outlet queries."""
        # First, ask about outlets in general
        decision1 = self.planner.plan_next_action("Is there an outlet in PJ?")
        
        # Should ask for more specific information
        assert decision1.action == ActionType.ASK
        assert "missing information" in decision1.reasoning.lower() or "query_type" in decision1.reasoning.lower()
        
        # Execute the first turn to build context
        self.planner.execute_conversation_turn("Is there an outlet in PJ?")
        
        # Now provide specific location
        decision2 = self.planner.plan_next_action("SS2, what time do you open?")
        
        # Should now plan to query the database
        assert decision2.action == ActionType.SQL_QUERY
        assert "SS2" in str(decision2.parameters.get("location_info", {}))
        assert "hours" in str(decision2.parameters.get("location_info", {}))
    
    def test_greeting_planning(self):
        """Test planning for greetings and conversation endings."""
        # Test greeting
        decision1 = self.planner.plan_next_action("Hello")
        assert decision1.action == ActionType.ASK
        assert "hello" in decision1.parameters.get("message", "").lower()
        
        # Test goodbye
        decision2 = self.planner.plan_next_action("Thanks, goodbye!")
        assert decision2.action == ActionType.END
        assert "ending" in decision2.reasoning.lower()
    
    def test_ask_action_for_incomplete_info(self):
        """Test that planner asks for clarification when information is incomplete."""
        incomplete_inputs = [
            "Calculate",  # Missing expression
            "Show me products",  # Could be more specific
            "What time?",  # Missing location
            "Where is it?"  # Missing context
        ]
        
        for incomplete_input in incomplete_inputs:
            decision = self.planner.plan_next_action(incomplete_input)
            # Should ask for more information or provide general help
            assert decision.action in [ActionType.ASK, ActionType.RAG_SEARCH]
    
    def test_conversation_turn_execution(self):
        """Test complete conversation turn execution."""
        result = self.planner.execute_conversation_turn("What's 10 + 5?")
        
        assert "user_input" in result
        assert "decision" in result
        assert "response" in result
        assert "memory_state" in result
        
        # Check that decision is correct
        assert result["decision"].action == ActionType.CALCULATE
        assert "10 + 5" in result["decision"].parameters.get("expression", "")
        
        # Check that memory was updated
        assert "10 + 5" in result["memory_state"]
    
    def test_context_aware_planning(self):
        """Test that planner uses conversation context for better decisions."""
        # Start a conversation about outlets
        self.planner.execute_conversation_turn("Is there an outlet in Petaling Jaya?")
        
        # Follow up with location - should be classified as outlet query due to context
        decision = self.planner.plan_next_action("SS2")
        
        # Should recognize this as continuation of outlet conversation
        assert decision.action in [ActionType.SQL_QUERY, ActionType.ASK]
        
        # If it's ASK, it should be asking for query type
        if decision.action == ActionType.ASK:
            assert "what would you like to know" in decision.parameters.get("message", "").lower()


class TestPlannerDecision:
    """Test suite for PlannerDecision data structure."""
    
    def test_planner_decision_creation(self):
        """Test creation and properties of PlannerDecision."""
        decision = PlannerDecision(
            action=ActionType.CALCULATE,
            reasoning="Test reasoning",
            parameters={"expression": "2+2"},
            confidence=0.9
        )
        
        assert decision.action == ActionType.CALCULATE
        assert decision.reasoning == "Test reasoning"
        assert decision.parameters["expression"] == "2+2"
        assert decision.confidence == 0.9
    
    def test_action_type_enum(self):
        """Test ActionType enum values."""
        assert ActionType.ASK.value == "ask"
        assert ActionType.CALCULATE.value == "calculate"
        assert ActionType.RAG_SEARCH.value == "rag_search"
        assert ActionType.SQL_QUERY.value == "sql_query"
        assert ActionType.END.value == "end"


class TestPlannerIntegration:
    """Integration tests for planner with memory system."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.planner = PlannerBot()
    
    def test_memory_integration(self):
        """Test that planner properly integrates with memory system."""
        # Execute several conversation turns
        inputs = [
            "Hello",
            "Is there an outlet in PJ?",
            "SS2",
            "What time do you open?"
        ]
        
        memory_states = []
        for user_input in inputs:
            result = self.planner.execute_conversation_turn(user_input)
            memory_states.append(result["memory_state"])
        
        # Memory should grow with each turn
        for i in range(1, len(memory_states)):
            assert len(memory_states[i]) > len(memory_states[i-1])
        
        # Final memory should contain all inputs
        final_memory = memory_states[-1]
        for user_input in inputs:
            assert user_input in final_memory or user_input.lower() in final_memory.lower()
    
    def test_context_dependent_decisions(self):
        """Test that decisions improve with conversation context."""
        # First turn - ambiguous input
        result1 = self.planner.execute_conversation_turn("SS2")
        decision1 = result1["decision"]
        
        # Should ask for clarification since no context
        assert decision1.action == ActionType.ASK
        
        # Build context about outlets
        self.planner.execute_conversation_turn("Is there an outlet in Petaling Jaya?")
        
        # Now the same input should be interpreted differently
        result2 = self.planner.execute_conversation_turn("SS2")
        decision2 = result2["decision"]
        
        # Should now understand this is about outlets
        assert decision2.action in [ActionType.SQL_QUERY, ActionType.ASK]
        if decision2.action == ActionType.ASK:
            # Should be asking for what info about SS2, not what SS2 is
            assert "what would you like to know" in decision2.parameters.get("message", "").lower()
    
    def test_planning_explanation(self):
        """Test that planner can explain its decision process."""
        explanation = self.planner.get_planning_explanation()
        
        assert "INTENT CLASSIFICATION" in explanation
        assert "INFORMATION EXTRACTION" in explanation
        assert "ACTION SELECTION" in explanation
        assert "CONFIDENCE SCORING" in explanation
        
        # Should mention all action types
        for action_type in ActionType:
            assert action_type.value.upper() in explanation or action_type.value in explanation


# Test runner for Phase 2
def run_phase2_tests():
    """
    Run all Phase 2 tests and display results.
    
    This function can be called to validate Phase 2 implementation
    before proceeding to Phase 3.
    """
    print("🧪 Running Phase 2 Test Suite...")
    print("=" * 50)
    
    # Run tests with pytest
    test_result = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ])
    
    if test_result == 0:
        print("\n✅ All Phase 2 tests passed!")
        print("🚀 Ready to proceed to Phase 3!")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        print("🔧 Fix issues before proceeding to Phase 3.")
    
    return test_result == 0


if __name__ == "__main__":
    run_phase2_tests() 