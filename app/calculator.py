"""
Calculator Service - Phase 3 Tool Integration
=============================================

Safe mathematical expression evaluation service with comprehensive error handling.
"""

import ast
import operator
import re
from typing import Union, Dict, Any
import math


class CalculatorService:
    """Safe calculator service for mathematical expression evaluation."""
    
    def __init__(self):
        """Initialize the calculator with supported operations."""
        # Supported binary operations
        self.binary_ops = {
            ast.Add: operator.add,       # +
            ast.Sub: operator.sub,       # -
            ast.Mult: operator.mul,      # *
            ast.Div: operator.truediv,   # /
            ast.Mod: operator.mod,       # %
            ast.Pow: operator.pow,       # ** or ^
        }
        
        # Supported unary operations
        self.unary_ops = {
            ast.UAdd: operator.pos,      # +x
            ast.USub: operator.neg,      # -x
        }
        
        # Supported mathematical functions
        self.functions = {
            'sqrt': math.sqrt,
            'abs': abs,
            'round': round,
        }
    
    def evaluate_expression(self, expression: str) -> Union[int, float]:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression string
            
        Returns:
            Numerical result of the expression
            
        Raises:
            ValueError: For invalid expressions or unsupported operations
            ZeroDivisionError: For division by zero
        """
        if not expression or not expression.strip():
            raise ValueError("Expression cannot be empty")
        
        # Clean and normalize the expression
        expression = self._normalize_expression(expression.strip())
        
        # Validate expression format
        self._validate_expression(expression)
        
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')
            
            # Evaluate the AST safely
            result = self._evaluate_node(tree.body)
            
            # Validate result
            if not isinstance(result, (int, float)):
                raise ValueError(f"Invalid result type: {type(result)}")
            
            if math.isnan(result):
                raise ValueError("Result is not a number")
            
            if math.isinf(result):
                raise ValueError("Result is infinite")
            
            return result
            
        except SyntaxError as e:
            raise ValueError(f"Invalid mathematical expression: {str(e)}")
        except (TypeError, AttributeError) as e:
            raise ValueError(f"Unsupported operation in expression: {str(e)}")
    
    def _normalize_expression(self, expression: str) -> str:
        """Normalize the expression for consistent parsing."""
        # Replace common alternative symbols
        expression = expression.replace('^', '**')  # Convert ^ to **
        expression = expression.replace('×', '*')   # Convert × to *
        expression = expression.replace('÷', '/')   # Convert ÷ to /
        
        # Remove extra whitespace
        expression = re.sub(r'\s+', ' ', expression)
        
        return expression
    
    def _validate_expression(self, expression: str) -> None:
        """Validate that the expression contains only allowed characters."""
        # Allow digits, operators, parentheses, decimal points
        allowed_pattern = r'^[0-9+\-*/().\s%*]+$'
        
        if not re.match(allowed_pattern, expression):
            raise ValueError("Expression contains invalid characters")
        
        # Check for potentially dangerous patterns
        dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open']
        
        expression_lower = expression.lower()
        for pattern in dangerous_patterns:
            if pattern in expression_lower:
                raise ValueError(f"Potentially dangerous pattern detected: {pattern}")
    
    def _evaluate_node(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            op = self.binary_ops.get(type(node.op))
            
            if not op:
                raise ValueError(f"Unsupported binary operation: {type(node.op)}")
            
            # Special handling for division by zero
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Division by zero")
            
            # Special handling for modulo by zero
            if isinstance(node.op, ast.Mod) and right == 0:
                raise ZeroDivisionError("Modulo by zero")
            
            result = op(left, right)
            
            # Ensure we don't return complex numbers
            if isinstance(result, complex):
                raise ValueError("Complex numbers are not supported")
            
            return result
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_node(node.operand)
            op = self.unary_ops.get(type(node.op))
            
            if not op:
                raise ValueError(f"Unsupported unary operation: {type(node.op)}")
            
            return op(operand)
        
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")


# Convenience function for quick calculations
def calculate(expression: str) -> Union[int, float]:
    """Quick calculation function for simple use cases."""
    calculator = CalculatorService()
    return calculator.evaluate_expression(expression)


# Example usage and testing
if __name__ == "__main__":
    # Test the calculator service
    calc = CalculatorService()
    
    test_expressions = [
        "2 + 3",
        "10 - 4", 
        "5 * 6",
        "15 / 3",
        "2 ** 3",
        "10 % 3",
        "(2 + 3) * 4",
        "2 + 3 * 4",  # Order of operations
    ]
    
    print("🧮 Calculator Service Test")
    print("=" * 30)
    
    for expr in test_expressions:
        try:
            result = calc.evaluate_expression(expr)
            print(f"✅ {expr} = {result}")
        except Exception as e:
            print(f"❌ {expr} → Error: {e}") 