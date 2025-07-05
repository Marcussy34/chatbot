"""
Chatbot Package - Mindhive AI Chatbot Engineer Assessment
=========================================================

This package contains the implementation for all phases of the
Mindhive AI Chatbot Engineer assessment.

Modules:
- memory_bot: Phase 1 - Sequential conversation with memory
- planner: Phase 2 - Agentic planning logic
- tools: Phase 3+ - Tool integration for calculator and APIs
"""

from .memory_bot import MemoryBot, SimpleLLM
from .planner import PlannerBot, ActionType, PlannerDecision, IntentClassifier
from .tools import ToolManager, CalculatorTool, calculate_expression

__version__ = "1.0.0"
__author__ = "Mindhive Assessment Candidate"

# Export main classes for easy import
__all__ = [
    "MemoryBot",
    "SimpleLLM",
    "PlannerBot", 
    "ActionType",
    "PlannerDecision",
    "IntentClassifier",
    "ToolManager",
    "CalculatorTool",
    "calculate_expression"
] 