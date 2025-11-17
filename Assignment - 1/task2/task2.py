from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import logfire
import os
import asyncio
import json
from typing import Any

load_dotenv()

# Configure Logfire
logfire.configure()
logfire.instrument_pydantic_ai()

# Available products (same as in UI)
AVAILABLE_PRODUCTS = [
    {"name": "Salt", "price": 2.50, "emoji": "🧂"},
    {"name": "Pepper", "price": 3.00, "emoji": "🌶️"},
    {"name": "Toothpaste", "price": 4.99, "emoji": "🦷"},
    {"name": "Toothbrush", "price": 3.50, "emoji": "🪥"},
    {"name": "Detergent", "price": 8.99, "emoji": "🧴"},
    {"name": "Soap", "price": 2.99, "emoji": "🧼"},
    {"name": "Shampoo", "price": 6.99, "emoji": "🧴"},
    {"name": "Paper Towels", "price": 5.49, "emoji": "🧻"},
]

async def manage_cart(ctx: RunContext[Any], product_name: str, action: str, quantity: int = 1, price: float = 0.0) -> str:
    """
    Manage shopping cart - add, remove, or update product quantity.
    
    Args:
        ctx: The run context from pydantic-ai
        product_name: The name of the product
        action: Action to perform - 'add', 'remove', or 'update'
        quantity: Quantity to add or set (default: 1)
        price: Optional price for custom items not in the product list (default: 0.0)
        
    Returns:
        JSON string with cart action details
    """
    with logfire.span('manage_cart', product_name=product_name, action=action, quantity=quantity):
        # Find product in available list
        product = next(
            (p for p in AVAILABLE_PRODUCTS if p["name"].lower() == product_name.lower()),
            None
        )
        
        # If product not found and action is add or update, allow custom item
        if not product and action in ['add', 'update']:
            logfire.info('Managing custom product', product_name=product_name, action=action, price=price, quantity=quantity)
            return json.dumps({
                "action": action,
                "product": product_name,
                "quantity": quantity,
                "price": price if price > 0 else 5.99,  # Default price for custom items
                "emoji": "📦",  # Default emoji for custom items
                "is_custom": True
            })
        
        if not product and action != 'remove':
            logfire.warn('Product not found', product_name=product_name)
            available = ', '.join([p['name'] for p in AVAILABLE_PRODUCTS])
            return f"Sorry, '{product_name}' is not available. Available: {available}"
        
        logfire.info('Cart action', product=product_name, action=action, quantity=quantity)
        
        # Return structured response
        return json.dumps({
            "action": action,
            "product": product["name"] if product else product_name,
            "quantity": quantity,
            "price": product["price"] if product else price if price > 0 else 5.99,
            "emoji": product["emoji"] if product else "📦",
            "is_custom": False if product else True
        })

model = "gemini-2.5-flash"
agent = Agent(
    model,
    tools=[manage_cart],
    system_prompt=(
        "You are a helpful shopping assistant. Use the manage_cart tool for all cart operations:\n"
        "- action='add' to add products (quantity defaults to 1)\n"
        "- action='remove' to remove products from cart\n"
        "- action='update' with the EXACT quantity parameter the user specifies to set specific quantity\n"
        "  * When user says 'update apple to 3', use action='update' with quantity=3\n"
        "  * When user says 'change banana quantity to 5', use action='update' with quantity=5\n"
        "  * When user says 'set orange to 2', use action='update' with quantity=2\n"
        "  * IMPORTANT: Use the EXACT number the user mentions in the quantity parameter\n"
        "Available products: Salt, Pepper, Toothpaste, Toothbrush, Detergent, Soap, Shampoo, Paper Towels.\n"
        "IMPORTANT: If a user requests an item not in the available list, you can still add it as a custom item.\n"
        "For custom items, estimate a reasonable price (use the price parameter). If you're unsure, use $5.99 as default.\n"
        "Be friendly and conversational in responses. Confirm the exact quantity when updating items."
    )
)

async def run_agent_with_logging(user_input: str, message_history: list):
    """Run the agent with Logfire logging for input and output."""
    with logfire.span('agent_interaction'):
        # Log user input
        logfire.info('User input received', user_input=user_input)
        
        # Run the agent with message history
        result = await agent.run(user_input, message_history=message_history)
        
        # Log agent output
        logfire.info('Agent output generated', agent_output=str(result.output))
        
    return result

async def main():
    message_history = []  # Initialize empty message history
    
    print("Chat with the agent (type 'exit', 'quit', or 'bye' to end)")
    print("-" * 60)
    
    while True:
        user_message = await asyncio.to_thread(input, "You: ")
        
        if user_message.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Run agent with logging
        result = await run_agent_with_logging(user_message, message_history)
        print(f"Agent: {result.output}")
        
        # Update message history with new messages from this run
        message_history = result.all_messages()
