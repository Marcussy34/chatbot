"""
Phase 1: Sequential Conversation - Memory-Based Chatbot
========================================================

This module implements a LangChain-based chatbot with memory capabilities
to track multi-turn conversations and maintain state across interactions.

Key Features:
- Uses ConversationBufferMemory for state tracking
- Handles the example conversation flow about outlets
- Maintains context across multiple turns
- Simple fallback responses when no specific intent is detected
"""

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.llms.base import LLM
from langchain.schema import Generation, LLMResult
from typing import List, Optional, Any
import re


class SimpleLLM(LLM):
    """
    Simple mock LLM for Phase 1 demonstration.
    
    This LLM implements basic conversation logic for the outlet inquiry example.
    In later phases, this will be replaced with actual LLM integration.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _get_outlets_db(self):
        """Get the outlets knowledge base."""
        return {
            "ss2": {
                "name": "SS2 Outlet",
                "location": "Petaling Jaya SS2",
                "opening_time": "9:00AM",
                "closing_time": "10:00PM",
                "services": ["dine-in", "takeaway", "delivery"]
            },
            "pj": {
                "outlets": ["SS2", "Damansara", "PJ Old Town"],
                "count": 3
            }
        }
    
    @property
    def _llm_type(self) -> str:
        return "simple_demo_llm"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Process the conversation prompt and generate appropriate responses.
        
        This method analyzes the conversation history and current input
        to provide contextually appropriate responses.
        """
        # Extract current input (last human message)
        lines = prompt.strip().split('\n')
        current_input = ""
        
        for line in reversed(lines):
            if line.startswith("Human: "):
                current_input = line.replace("Human: ", "").lower()
                break
        
        # Response logic based on conversation patterns
        return self._generate_response(current_input, prompt)
    
    def _generate_response(self, current_input: str, full_prompt: str) -> str:
        """
        Generate responses based on current input and conversation history.
        
        Args:
            current_input: The latest user message
            full_prompt: Complete conversation history
            
        Returns:
            Appropriate response string
        """
        current_input = current_input.strip()
        
        # Check for outlet location inquiries
        if "outlet" in current_input and any(location in current_input for location in ["pj", "petaling jaya"]):
            return "Yes! We have several outlets in Petaling Jaya. Which outlet are you referring to?"
        
        # Check for specific outlet inquiries (SS2)
        if "ss2" in current_input:
            if any(time_word in current_input for time_word in ["time", "open", "opening", "hour"]):
                return "Ah yes, the SS2 outlet opens at 9:00AM and closes at 10:00PM."
            else:
                return "The SS2 outlet is located in Petaling Jaya SS2. What would you like to know about it?"
        
        # Check for general opening time questions
        if any(time_word in current_input for time_word in ["time", "open", "opening", "hour"]):
            if "ss2" in full_prompt.lower():
                return "The SS2 outlet opens at 9:00AM and closes at 10:00PM."
            else:
                return "Which outlet's opening time would you like to know?"
        
        # Check for greetings
        if any(greeting in current_input for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm here to help you with information about our outlets. How can I assist you today?"
        
        # Default response for unrecognized inputs
        return "I'd be happy to help you with outlet information! You can ask about locations, opening times, or services."
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """Generate responses for multiple prompts."""
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop)
            generations.append([Generation(text=response)])
        return LLMResult(generations=generations)


class MemoryBot:
    """
    Main chatbot class implementing Phase 1 requirements.
    
    Features:
    - Multi-turn conversation tracking using ConversationBufferMemory
    - State management across conversation turns
    - Example conversation flow implementation
    """
    
    def __init__(self):
        """Initialize the memory-based chatbot."""
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=False,
            human_prefix="Human",
            ai_prefix="AI"
        )
        
        # Initialize simple LLM
        self.llm = SimpleLLM()
        
        # Create conversation chain with memory
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=True
        )
        
        print("🤖 Memory Bot initialized! Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("💭 I can remember our conversation across multiple turns.")
        print("🏪 Try asking about outlets in Petaling Jaya!\n")
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and return bot response.
        
        Args:
            user_input: User's message
            
        Returns:
            Bot's response string
        """
        try:
            response = self.conversation.predict(input=user_input)
            return response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try again."
    
    def get_memory_contents(self) -> str:
        """
        Get current conversation history from memory.
        
        Returns:
            String representation of conversation history
        """
        return self.memory.buffer
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        print("🧹 Memory cleared!")
    
    def run_interactive(self):
        """
        Run interactive chat session.
        
        This method demonstrates the Phase 1 requirements by allowing
        users to have multi-turn conversations with memory persistence.
        """
        print("🚀 Starting interactive chat session...")
        print("📝 Example conversation to try:")
        print("   1. 'Is there an outlet in Petaling Jaya?'")
        print("   2. 'SS2, what's the opening time?'")
        print("   3. 'What services do you offer?'\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                # Check for memory commands
                if user_input.lower() == 'show memory':
                    print(f"📚 Memory contents: {self.get_memory_contents()}")
                    continue
                
                if user_input.lower() == 'clear memory':
                    self.clear_memory()
                    continue
                
                # Get bot response
                if user_input:
                    response = self.chat(user_input)
                    print(f"Bot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")


def run_example_conversation():
    """
    Run the example conversation from the assessment requirements.
    
    This function demonstrates the exact conversation flow specified
    in the Phase 1 requirements.
    """
    print("🎯 Running Phase 1 Example Conversation:")
    print("=" * 50)
    
    bot = MemoryBot()
    
    # Example conversation sequence
    conversation_steps = [
        "Is there an outlet in Petaling Jaya?",
        "SS2, what's the opening time?",
        "What services do you offer there?"
    ]
    
    for i, user_input in enumerate(conversation_steps, 1):
        print(f"\n🔄 Turn {i}:")
        print(f"User: {user_input}")
        
        response = bot.chat(user_input)
        print(f"Bot: {response}")
        
        # Show memory state after each turn
        print(f"💭 Memory state: {len(bot.get_memory_contents().split())} words stored")
    
    print("\n✅ Example conversation completed!")
    print(f"📚 Final memory contents:\n{bot.get_memory_contents()}")


if __name__ == "__main__":
    """
    Main entry point for Phase 1 demonstration.
    
    Users can choose to run the example conversation or start
    an interactive session.
    """
    print("🧠 Mindhive AI Chatbot - Phase 1: Sequential Conversation")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Run example conversation")
        print("2. Start interactive chat")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_example_conversation()
        elif choice == "2":
            bot = MemoryBot()
            bot.run_interactive()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.") 