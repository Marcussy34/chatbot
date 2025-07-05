"""
Phase 2: Agentic Planning - Planner/Controller Logic
====================================================

This module implements the core planning logic that determines the bot's next action
based on intent parsing, conversation context, and missing information detection.

Key Features:
- Intent classification (math, product search, outlet queries, etc.)
- Action selection (ASK, CALCULATE, RAG_SEARCH, SQL_QUERY, END)
- Context-aware decision making using conversation memory
- Extensible framework for tool integration in later phases
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import re
from dataclasses import dataclass

from .memory_bot import MemoryBot


class ActionType(Enum):
    """
    Enumeration of possible actions the planner can decide to take.
    
    ASK: Ask a follow-up question to gather missing information
    CALCULATE: Perform mathematical calculation using calculator tool
    RAG_SEARCH: Search product knowledge base using RAG
    SQL_QUERY: Query outlet database using Text2SQL
    END: Conversation is complete, no further action needed
    """
    ASK = "ask"
    CALCULATE = "calculate" 
    RAG_SEARCH = "rag_search"
    SQL_QUERY = "sql_query"
    END = "end"


@dataclass
class PlannerDecision:
    """
    Represents a planning decision with action type and reasoning.
    
    Attributes:
        action: The type of action to take
        reasoning: Human-readable explanation of why this action was chosen
        parameters: Additional parameters for the action (e.g., query text, calculation)
        confidence: Confidence score (0.0 to 1.0) for the decision
    """
    action: ActionType
    reasoning: str
    parameters: Dict[str, Any]
    confidence: float


class IntentClassifier:
    """
    Classifies user intent based on input text and conversation context.
    
    Uses rule-based pattern matching for reliability and transparency.
    Can be extended with ML-based classification in future iterations.
    """
    
    def __init__(self):
        """Initialize the intent classifier with pattern definitions."""
        # Mathematical expression patterns
        self.math_patterns = [
            r'\d+\s*[\+\-\*\/\%\^]\s*\d+',  # Basic arithmetic: 2+3, 10*5, etc.
            r'calculate|math|compute|solve',   # Explicit calculation requests
            r'what\s+is\s+\d+.*[\+\-\*\/].*\d+',  # "What is 5 + 3?"
            r'\d+\s*\^\s*\d+',  # Exponentiation: 2^3
            r'sqrt|square\s+root|log|sin|cos|tan'  # Mathematical functions
        ]
        
        # Product search patterns
        self.product_patterns = [
            r'product|item|buy|purchase|shop',
            r'tumbler|cup|mug|bottle|drinkware',
            r'zus.*coffee|coffee.*zus',
            r'what.*sell|what.*available|what.*have',
            r'recommend|suggest|best.*for'
        ]
        
        # Outlet/location query patterns
        self.outlet_patterns = [
            r'outlet|store|location|branch',
            r'where.*is|where.*can.*find',
            r'opening.*time|hours|when.*open|when.*close',
            r'address|direction|how.*get.*there',
            r'petaling\s+jaya|pj|ss2|damansara|kl|kuala\s+lumpur'
        ]
        
        # Greeting and conversation end patterns
        self.greeting_patterns = [
            r'^(hi|hello|hey|good\s+(morning|afternoon|evening))',
            r'(thank\s+you|thanks|bye|goodbye|see\s+you)'
        ]
    
    def classify_intent(self, user_input: str, conversation_history: str = "") -> Tuple[str, float]:
        """
        Classify the intent of user input.
        
        Args:
            user_input: The user's current message
            conversation_history: Previous conversation context
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        user_input_lower = user_input.lower().strip()
        
        # Check for mathematical intent
        if self._matches_patterns(user_input_lower, self.math_patterns):
            return "calculation", 0.9
        
        # Check for product search intent
        if self._matches_patterns(user_input_lower, self.product_patterns):
            return "product_search", 0.8
        
        # Check for outlet/location intent
        if self._matches_patterns(user_input_lower, self.outlet_patterns):
            return "outlet_query", 0.8
        
        # Check for greetings
        if self._matches_patterns(user_input_lower, self.greeting_patterns):
            return "greeting", 0.9
        
        # Context-based classification using conversation history
        if conversation_history:
            return self._classify_with_context(user_input_lower, conversation_history)
        
        # Default to general inquiry
        return "general", 0.5
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given regex patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _classify_with_context(self, user_input: str, history: str) -> Tuple[str, float]:
        """
        Use conversation context to improve intent classification.
        
        Args:
            user_input: Current user input
            history: Conversation history
            
        Returns:
            Tuple of (intent_type, confidence_score)
        """
        history_lower = history.lower()
        
        # If previous conversation was about outlets and user gives a location
        if any(word in history_lower for word in ['outlet', 'store', 'location']):
            if any(word in user_input for word in ['ss2', 'pj', 'damansara', 'time', 'hour']):
                return "outlet_query", 0.9
        
        # If previous conversation was about products and user gives specifications
        if any(word in history_lower for word in ['product', 'tumbler', 'coffee']):
            return "product_search", 0.8
        
        # If user provides additional context after a question
        if '?' in history_lower and len(user_input.split()) <= 3:
            return "context_addition", 0.7
        
        return "general", 0.5


class InformationExtractor:
    """
    Extracts specific information and identifies missing data from user input.
    """
    
    def extract_calculation_expression(self, user_input: str) -> Optional[str]:
        """
        Extract mathematical expression from user input.
        
        Args:
            user_input: User's message
            
        Returns:
            Mathematical expression string or None
        """
        # Look for mathematical expressions
        math_match = re.search(r'(\d+(?:\.\d+)?\s*[\+\-\*\/\%\^]\s*\d+(?:\.\d+)?)', user_input)
        if math_match:
            return math_match.group(1)
        
        # Look for "what's X" patterns (handle contractions)
        whats_match = re.search(r'what[\'s]*\s+(.+)', user_input, re.IGNORECASE)
        if whats_match:
            expression = whats_match.group(1).strip()
            if re.search(r'\d+.*[\+\-\*\/].*\d+', expression):
                return expression
        
        # Look for "what is X" patterns
        what_is_match = re.search(r'what\s+is\s+(.+)', user_input, re.IGNORECASE)
        if what_is_match:
            expression = what_is_match.group(1).strip()
            if re.search(r'\d+.*[\+\-\*\/].*\d+', expression):
                return expression
        
        # Look for "calculate X" patterns
        calc_match = re.search(r'calculate\s+(.+)', user_input, re.IGNORECASE)
        if calc_match:
            expression = calc_match.group(1).strip()
            if re.search(r'\d+.*[\+\-\*\/].*\d+', expression):
                return expression
        
        return None
    
    def extract_location_info(self, user_input: str) -> Dict[str, str]:
        """
        Extract location-related information from user input.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with location details
        """
        info = {}
        user_input_lower = user_input.lower()
        
        # Extract specific locations
        if 'ss2' in user_input_lower:
            info['location'] = 'SS2'
        elif any(loc in user_input_lower for loc in ['pj', 'petaling jaya']):
            info['area'] = 'Petaling Jaya'
        elif any(loc in user_input_lower for loc in ['kl', 'kuala lumpur']):
            info['area'] = 'Kuala Lumpur'
        
        # Extract query type
        if any(word in user_input_lower for word in ['time', 'hour', 'open', 'close']):
            info['query_type'] = 'hours'
        elif any(word in user_input_lower for word in ['address', 'where', 'direction']):
            info['query_type'] = 'location'
        elif any(word in user_input_lower for word in ['service', 'offer', 'available']):
            info['query_type'] = 'services'
        
        return info
    
    def identify_missing_info(self, intent: str, extracted_info: Dict[str, Any], 
                            conversation_history: str) -> List[str]:
        """
        Identify what information is missing for completing the user's request.
        
        Args:
            intent: Classified intent type
            extracted_info: Information extracted from current input
            conversation_history: Previous conversation context
            
        Returns:
            List of missing information items
        """
        missing = []
        
        if intent == "outlet_query":
            if not extracted_info.get('location') and not extracted_info.get('area'):
                if 'outlet' in conversation_history.lower():
                    missing.append("specific_location")
                else:
                    missing.append("location")
            
            if not extracted_info.get('query_type'):
                missing.append("query_type")
        
        elif intent == "product_search":
            # For product searches, we can be more flexible
            # but might ask for specific preferences
            if len(extracted_info) == 0:
                missing.append("product_preferences")
        
        elif intent == "calculation":
            # Check if we have a valid mathematical expression
            expression = self.extract_calculation_expression(extracted_info.get('text', ''))
            if not expression:
                missing.append("mathematical_expression")
        
        return missing


class PlannerBot:
    """
    Main planner bot that integrates memory, intent classification, and action selection.
    
    This class extends the memory bot functionality with intelligent planning
    capabilities to decide the next best action in a conversation.
    """
    
    def __init__(self):
        """Initialize the planner bot with memory and classification components."""
        self.memory_bot = MemoryBot()
        self.intent_classifier = IntentClassifier()
        self.info_extractor = InformationExtractor()
        
        print("🧠 Planner Bot initialized!")
        print("🎯 I can analyze intent and plan next actions:")
        print("   • ASK follow-up questions")
        print("   • CALCULATE mathematical expressions") 
        print("   • SEARCH product information")
        print("   • QUERY outlet data")
        print("   • END completed conversations\n")
    
    def plan_next_action(self, user_input: str) -> PlannerDecision:
        """
        Analyze user input and conversation context to plan the next action.
        
        Args:
            user_input: The user's current message
            
        Returns:
            PlannerDecision with action type, reasoning, and parameters
        """
        # Get conversation history from memory
        conversation_history = self.memory_bot.get_memory_contents()
        
        # Classify intent
        intent, confidence = self.intent_classifier.classify_intent(user_input, conversation_history)
        
        # Extract information based on intent
        if intent == "calculation":
            expression = self.info_extractor.extract_calculation_expression(user_input)
            extracted_info = {"expression": expression, "text": user_input}
        elif intent == "outlet_query":
            extracted_info = self.info_extractor.extract_location_info(user_input)
            extracted_info["text"] = user_input
        else:
            extracted_info = {"text": user_input}
        
        # Identify missing information
        missing_info = self.info_extractor.identify_missing_info(intent, extracted_info, conversation_history)
        
        # Make planning decision
        return self._make_decision(intent, confidence, extracted_info, missing_info, conversation_history)
    
    def _make_decision(self, intent: str, confidence: float, extracted_info: Dict[str, Any], 
                      missing_info: List[str], conversation_history: str) -> PlannerDecision:
        """
        Make the final planning decision based on analyzed information.
        
        Args:
            intent: Classified intent type
            confidence: Classification confidence
            extracted_info: Extracted information from input
            missing_info: List of missing information
            conversation_history: Previous conversation context
            
        Returns:
            PlannerDecision with chosen action
        """
        # If information is missing, ask for clarification
        if missing_info:
            return self._plan_ask_action(intent, missing_info, extracted_info)
        
        # If we have complete information, choose appropriate action
        if intent == "calculation" and extracted_info.get("expression"):
            return PlannerDecision(
                action=ActionType.CALCULATE,
                reasoning=f"Mathematical expression detected: '{extracted_info['expression']}'. Ready to calculate.",
                parameters={"expression": extracted_info["expression"]},
                confidence=confidence
            )
        
        elif intent == "product_search":
            return PlannerDecision(
                action=ActionType.RAG_SEARCH,
                reasoning="Product inquiry detected. Will search product knowledge base.",
                parameters={"query": extracted_info.get("text", "")},
                confidence=confidence
            )
        
        elif intent == "outlet_query":
            return PlannerDecision(
                action=ActionType.SQL_QUERY,
                reasoning="Outlet/location query detected. Will query outlet database.",
                parameters={"location_info": extracted_info},
                confidence=confidence
            )
        
        elif intent == "greeting":
            text = extracted_info.get("text", "").lower()
            if any(word in text for word in ["bye", "goodbye", "thanks", "thank you"]):
                return PlannerDecision(
                    action=ActionType.END,
                    reasoning="Conversation ending detected.",
                    parameters={},
                    confidence=confidence
                )
            else:
                return PlannerDecision(
                    action=ActionType.ASK,
                    reasoning="Greeting detected. Will respond and ask how to help.",
                    parameters={"message": "Hello! How can I help you today?"},
                    confidence=confidence
                )
        
        # Default: Ask for more information
        return PlannerDecision(
            action=ActionType.ASK,
            reasoning="Intent unclear or insufficient information. Will ask for clarification.",
            parameters={"message": "I'd be happy to help! Could you please provide more details about what you're looking for?"},
            confidence=0.5
        )
    
    def _plan_ask_action(self, intent: str, missing_info: List[str], extracted_info: Dict[str, Any]) -> PlannerDecision:
        """
        Plan an ASK action to gather missing information.
        
        Args:
            intent: The classified intent
            missing_info: List of missing information items
            extracted_info: Already extracted information
            
        Returns:
            PlannerDecision for ASK action
        """
        if "specific_location" in missing_info:
            message = "Which specific outlet are you asking about?"
        elif "location" in missing_info:
            message = "Which location or area are you interested in?"
        elif "query_type" in missing_info:
            message = "What would you like to know about the outlet? (hours, location, services)"
        elif "mathematical_expression" in missing_info:
            message = "What calculation would you like me to perform?"
        elif "product_preferences" in missing_info:
            message = "What type of product are you looking for?"
        else:
            message = "Could you please provide more details?"
        
        return PlannerDecision(
            action=ActionType.ASK,
            reasoning=f"Missing information: {', '.join(missing_info)}. Need to ask follow-up question.",
            parameters={"message": message},
            confidence=0.8
        )
    
    def execute_conversation_turn(self, user_input: str) -> Dict[str, Any]:
        """
        Execute a complete conversation turn: plan, act, and respond.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with planning decision and response
        """
        # Plan the next action
        decision = self.plan_next_action(user_input)
        
        # For now, simulate action execution (actual execution in Phase 3+)
        if decision.action == ActionType.ASK:
            response = decision.parameters.get("message", "How can I help you?")
        elif decision.action == ActionType.CALCULATE:
            response = f"I would calculate: {decision.parameters.get('expression', 'N/A')} (Calculator tool will be integrated in Phase 3)"
        elif decision.action == ActionType.RAG_SEARCH:
            response = f"I would search for: '{decision.parameters.get('query', 'N/A')}' (RAG search will be integrated in Phase 4)"
        elif decision.action == ActionType.SQL_QUERY:
            response = f"I would query outlet database for: {decision.parameters.get('location_info', {})} (SQL query will be integrated in Phase 4)"
        elif decision.action == ActionType.END:
            response = "Thank you! Have a great day!"
        else:
            response = "I'm not sure how to help with that. Could you please clarify?"
        
        # Update memory with the conversation
        self.memory_bot.chat(user_input)
        
        return {
            "user_input": user_input,
            "decision": decision,
            "response": response,
            "memory_state": self.memory_bot.get_memory_contents()
        }
    
    def get_planning_explanation(self) -> str:
        """
        Get a detailed explanation of the planning process and decision points.
        
        Returns:
            Multi-line string explaining the planner's decision logic
        """
        return """
🧠 Planner Decision Process:

1. INTENT CLASSIFICATION:
   • Mathematical expressions → CALCULATE action
   • Product queries → RAG_SEARCH action  
   • Outlet/location queries → SQL_QUERY action
   • Greetings/endings → ASK or END action

2. INFORMATION EXTRACTION:
   • Parse specific entities (locations, expressions, etc.)
   • Use conversation context for disambiguation
   • Identify what information is still missing

3. ACTION SELECTION:
   • ASK: When information is incomplete
   • CALCULATE: When math expression is ready
   • RAG_SEARCH: When product query is complete
   • SQL_QUERY: When location query is complete  
   • END: When conversation is finished

4. CONFIDENCE SCORING:
   • Pattern matching confidence (0.5-0.9)
   • Context-based adjustments
   • Missing information penalties

This framework extends to tool integration in later phases.
        """.strip()


# Convenience function for quick testing
def demo_planner_decisions():
    """
    Demonstrate the planner's decision-making with various inputs.
    """
    planner = PlannerBot()
    
    test_inputs = [
        "Hello",
        "Is there an outlet in PJ?",
        "SS2",
        "What's 5 + 3?",
        "What products do you have?",
        "Thanks, goodbye!"
    ]
    
    print("🎯 Planner Decision Demo:")
    print("=" * 40)
    
    for user_input in test_inputs:
        print(f"\n📝 Input: '{user_input}'")
        decision = planner.plan_next_action(user_input)
        print(f"🎯 Action: {decision.action.value}")
        print(f"💭 Reasoning: {decision.reasoning}")
        print(f"📊 Confidence: {decision.confidence:.1f}")


if __name__ == "__main__":
    demo_planner_decisions() 