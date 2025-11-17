from fasthtml.common import *
import asyncio
from task2 import run_agent_with_logging
import json
from starlette.requests import Request

app, rt = fast_app(
    hdrs=(
        Script(src="https://unpkg.com/htmx.org@1.9.10"),
    )
)

# Session storage - per user session
sessions = {}

def get_session_id(request: Request):
    """Get or create session ID from cookie"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    return session_id

def get_session_data(session_id: str):
    """Get session data, create if doesn't exist"""
    if session_id not in sessions:
        sessions[session_id] = {
            'messages': [],
            'agent_message_history': [],
            'cart': {}
        }
    return sessions[session_id]

# Available products
products = [
    {"name": "Salt", "price": 2.50, "emoji": "🧂"},
    {"name": "Pepper", "price": 3.00, "emoji": "🌶️"},
    {"name": "Toothpaste", "price": 4.99, "emoji": "🦷"},
    {"name": "Toothbrush", "price": 3.50, "emoji": "🪥"},
    {"name": "Detergent", "price": 8.99, "emoji": "🧴"},
    {"name": "Soap", "price": 2.99, "emoji": "🧼"},
    {"name": "Shampoo", "price": 6.99, "emoji": "🧴"},
    {"name": "Paper Towels", "price": 5.49, "emoji": "🧻"},
]

# Product card no longer needed - products shown in sidebar

def CartItem(name, price, emoji, quantity):
    """Create a cart item card with quantity controls"""
    return Div(
        Div(
            Span(emoji, cls="cart-item-emoji"),
            Div(
                Div(name, cls="cart-item-name"),
                Div(f"${price:.2f}", cls="cart-item-price"),
                cls="cart-item-info"
            ),
            cls="cart-item-header"
        ),
        Div(
            Button("-", 
                hx_post=f"/cart/decrease/{name}",
                hx_target="#cart-items",
                hx_swap="innerHTML",
                cls="qty-button"
            ),
            Span(str(quantity), cls="qty-value"),
            Button("+",
                hx_post=f"/cart/increase/{name}",
                hx_target="#cart-items",
                hx_swap="innerHTML",
                cls="qty-button"
            ),
            cls="cart-item-controls"
        ),
        cls="cart-item"
    )

def ChatMessage(text, is_user=False):
    """Create a chat message in ChatGPT style"""
    wrapper_class = "message-wrapper user" if is_user else "message-wrapper bot"
    avatar_class = "avatar user" if is_user else "avatar bot"
    avatar_text = "U" if is_user else "AI"
    
    return Div(
        Div(avatar_text, cls=avatar_class),
        Div(
            Div(text, cls="message-text"),
            cls="message-content"
        ),
        cls=wrapper_class,
        style="animation: fadeIn 0.3s;"
    )

@rt("/")
def get(request: Request):
    """Main chat page"""
    session_id = get_session_id(request)
    # Initialize session data
    get_session_data(session_id)
    
    response = Html(
        Head(
            Title("Shopping Assistant"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
            Style("""
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: #0f1419;
                    height: 100vh;
                    display: flex;
                    color: #e7eaed;
                    overflow: hidden;
                }
                
                .main-wrapper {
                    display: flex;
                    width: 100%;
                    height: 100vh;
                }
                
                .main-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    max-width: 1200px;
                    margin: 0 auto;
                    width: 100%;
                }
                
                .chat-header {
                    padding: 20px 32px;
                    border-bottom: 1px solid #2f3336;
                    background: linear-gradient(180deg, #171717 0%, #1a1a1a 100%);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }
                
                .header-left {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .logo {
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, #10a37f 0%, #16c79a 100%);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    font-weight: 700;
                    color: white;
                    position: relative;
                    overflow: hidden;
                }
                
                .logo::before {
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: linear-gradient(
                        45deg,
                        transparent,
                        rgba(255, 255, 255, 0.1),
                        transparent
                    );
                    animation: shimmer 3s infinite;
                }
                
                @keyframes shimmer {
                    0% {
                        transform: translateX(-100%) translateY(-100%) rotate(45deg);
                    }
                    100% {
                        transform: translateX(100%) translateY(100%) rotate(45deg);
                    }
                }
                
                .header-info {
                    display: flex;
                    flex-direction: column;
                }
                
                .chat-title {
                    font-size: 16px;
                    font-weight: 600;
                    color: #e7eaed;
                }
                
                .chat-subtitle {
                    font-size: 12px;
                    color: #8b98a5;
                    margin-top: 2px;
                }
                
                .header-badge {
                    padding: 6px 12px;
                    background: #2f3336;
                    border-radius: 16px;
                    font-size: 11px;
                    color: #10a37f;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .chat-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 32px;
                    display: flex;
                    flex-direction: column;
                    gap: 28px;
                }
                
                .welcome-message {
                    text-align: center;
                    padding: 60px 20px;
                    max-width: 600px;
                    margin: 0 auto;
                }
                
                .welcome-icon {
                    font-size: 56px;
                    margin-bottom: 24px;
                    animation: float 3s ease-in-out infinite;
                }
                
                @keyframes float {
                    0%, 100% {
                        transform: translateY(0);
                    }
                    50% {
                        transform: translateY(-10px);
                    }
                }
                
                .welcome-title {
                    font-size: 28px;
                    font-weight: 700;
                    color: #e7eaed;
                    margin-bottom: 12px;
                    background: linear-gradient(135deg, #10a37f 0%, #3b82f6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .welcome-text {
                    font-size: 14px;
                    color: #8b98a5;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }
                
                .quick-prompts {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 12px;
                    margin-top: 24px;
                }
                
                .prompt-card {
                    padding: 16px;
                    background: #2f3336;
                    border-radius: 10px;
                    text-align: left;
                    cursor: pointer;
                    transition: all 0.2s;
                    border: 1px solid transparent;
                }
                
                .prompt-card:hover {
                    background: #3a3f44;
                    border-color: #10a37f;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.2);
                }
                
                .prompt-card:active {
                    transform: translateY(0);
                }
                
                .prompt-icon {
                    font-size: 20px;
                    margin-bottom: 8px;
                }
                
                .prompt-text {
                    font-size: 13px;
                    color: #e7eaed;
                    font-weight: 500;
                }
                
                .message-wrapper {
                    display: flex;
                    gap: 16px;
                    max-width: 100%;
                }
                
                .message-wrapper.user {
                    flex-direction: row-reverse;
                    justify-content: flex-start;
                }
                
                .message-wrapper.bot {
                    justify-content: flex-start;
                }
                
                .avatar {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                
                .avatar.bot {
                    background: linear-gradient(135deg, #10a37f 0%, #16c79a 100%);
                    color: white;
                }
                
                .avatar.user {
                    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
                    color: white;
                }
                
                .message-content {
                    flex: 0 1 auto;
                    min-width: 0;
                    max-width: 75%;
                }
                
                .message-text {
                    padding: 16px 18px;
                    border-radius: 14px;
                    line-height: 1.6;
                    font-size: 14px;
                    word-wrap: break-word;
                    display: inline-block;
                    width: 100%;
                }
                
                .message-wrapper.bot .message-text {
                    background: #2f3336;
                    color: #e7eaed;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                }
                
                .message-wrapper.user .message-text {
                    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
                    color: white;
                    box-shadow: 0 2px 12px rgba(59, 130, 246, 0.3);
                }
                
                .typing-indicator {
                    display: flex;
                    gap: 16px;
                    max-width: 100%;
                    animation: fadeIn 0.3s;
                }
                
                .typing-indicator .avatar {
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    font-size: 16px;
                    font-weight: 600;
                    background: linear-gradient(135deg, #10a37f 0%, #16c79a 100%);
                    color: white;
                }
                
                .typing-indicator .message-content {
                    flex: 1;
                    min-width: 0;
                }
                
                .typing-indicator .message-text {
                    padding: 16px 18px;
                    border-radius: 14px;
                    background: #2f3336;
                    display: inline-flex;
                    gap: 4px;
                    align-items: center;
                }
                
                .typing-dot {
                    width: 8px;
                    height: 8px;
                    background: #8b98a5;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }
                
                .typing-dot:nth-child(1) {
                    animation-delay: 0s;
                }
                
                .typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                        opacity: 0.4;
                    }
                    30% {
                        transform: translateY(-8px);
                        opacity: 1;
                    }
                }
                
                .chat-input-container {
                    padding: 24px 32px 32px;
                    background: #171717;
                    border-top: 1px solid #2f3336;
                }
                
                .input-wrapper {
                    max-width: 900px;
                    margin: 0 auto;
                    position: relative;
                    display: flex;
                    align-items: center;
                    background: #2f3336;
                    border-radius: 28px;
                    padding: 6px 6px 6px 24px;
                    transition: all 0.2s;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                
                .input-wrapper:focus-within {
                    background: #3a3f44;
                    box-shadow: 0 0 0 2px #10a37f, 0 6px 16px rgba(0, 0, 0, 0.4);
                }
                
                .input-wrapper.loading {
                    opacity: 0.6;
                    pointer-events: none;
                }
                
                .chat-input {
                    flex: 1;
                    padding: 12px 0;
                    background: transparent;
                    border: none;
                    outline: none;
                    color: #e7eaed;
                    font-size: 15px;
                    font-family: inherit;
                    resize: none;
                    max-height: 200px;
                }
                
                .chat-input::placeholder {
                    color: #8b98a5;
                }
                
                .chat-input:disabled {
                    cursor: not-allowed;
                }
                
                .send-button {
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, #10a37f 0%, #16c79a 100%);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                    flex-shrink: 0;
                    font-size: 18px;
                    font-weight: 700;
                    box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
                }
                
                .send-button:hover:not(:disabled) {
                    background: linear-gradient(135deg, #0d8c6c 0%, #13a885 100%);
                    transform: scale(1.05);
                    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.4);
                }
                
                .send-button:active:not(:disabled) {
                    transform: scale(0.95);
                }
                
                .send-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                
                .loading-dots {
                    display: none;
                }
                
                .loading-dots.active {
                    display: flex;
                    gap: 4px;
                    align-items: center;
                    justify-content: center;
                }
                
                .loading-dot {
                    width: 6px;
                    height: 6px;
                    background: white;
                    border-radius: 50%;
                    animation: bounce 1.4s infinite ease-in-out both;
                }
                
                .loading-dot:nth-child(1) {
                    animation-delay: -0.32s;
                }
                
                .loading-dot:nth-child(2) {
                    animation-delay: -0.16s;
                }
                
                @keyframes bounce {
                    0%, 80%, 100% {
                        transform: scale(0);
                        opacity: 0.5;
                    }
                    40% {
                        transform: scale(1);
                        opacity: 1;
                    }
                }
                
                .cart-sidebar {
                    width: 360px;
                    background: #171717;
                    border-left: 1px solid #2f3336;
                    display: flex;
                    flex-direction: column;
                }
                
                .cart-header {
                    padding: 24px 20px;
                    border-bottom: 1px solid #2f3336;
                }
                
                .cart-title {
                    font-size: 16px;
                    font-weight: 600;
                    color: #e7eaed;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin-bottom: 8px;
                }
                
                .cart-count {
                    font-size: 12px;
                    color: #8b98a5;
                }
                
                .cart-items {
                    flex: 1;
                    overflow-y: auto;
                    padding: 20px;
                }
                
                .cart-empty {
                    text-align: center;
                    color: #8b98a5;
                    padding: 80px 20px;
                    font-size: 13px;
                    line-height: 1.8;
                }
                
                .cart-empty-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                    opacity: 0.5;
                }
                
                .cart-item {
                    background: #2f3336;
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 1px solid transparent;
                    animation: slideIn 0.3s ease-out;
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateX(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                
                .cart-item:hover {
                    background: #3a3f44;
                    border-color: #10a37f;
                    transform: translateX(-4px);
                    box-shadow: 4px 0 12px rgba(16, 163, 127, 0.2);
                }
                
                .cart-item-header {
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    margin-bottom: 12px;
                }
                
                .cart-item-emoji {
                    font-size: 28px;
                }
                
                .cart-item-info {
                    flex: 1;
                }
                
                .cart-item-name {
                    font-size: 14px;
                    font-weight: 600;
                    color: #e7eaed;
                    margin-bottom: 4px;
                }
                
                .cart-item-price {
                    font-size: 13px;
                    color: #10a37f;
                    font-weight: 600;
                }
                
                .cart-item-controls {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 14px;
                }
                
                .qty-button {
                    width: 32px;
                    height: 32px;
                    background: #3a3f44;
                    color: #e7eaed;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .qty-button:hover {
                    background: #10a37f;
                    color: white;
                    transform: scale(1.1);
                }
                
                .qty-button:active {
                    transform: scale(0.95);
                }
                
                .qty-value {
                    font-size: 15px;
                    font-weight: 600;
                    color: #e7eaed;
                    min-width: 28px;
                    text-align: center;
                }
                
                .cart-footer {
                    padding: 20px;
                    border-top: 1px solid #2f3336;
                    background: #1a1a1a;
                }
                
                .cart-total {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                }
                
                .total-label {
                    font-size: 14px;
                    color: #8b98a5;
                    font-weight: 500;
                }
                
                .total-amount {
                    font-size: 20px;
                    color: #10a37f;
                    font-weight: 700;
                }
                
                .checkout-button {
                    width: 100%;
                    padding: 14px;
                    background: linear-gradient(135deg, #10a37f 0%, #16c79a 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
                }
                
                .checkout-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(16, 163, 127, 0.4);
                }
                
                .checkout-button:active {
                    transform: translateY(0);
                }
                
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                .chat-messages::-webkit-scrollbar,
                .cart-items::-webkit-scrollbar {
                    width: 8px;
                }
                
                .chat-messages::-webkit-scrollbar-track,
                .cart-items::-webkit-scrollbar-track {
                    background: transparent;
                }
                
                .chat-messages::-webkit-scrollbar-thumb,
                .cart-items::-webkit-scrollbar-thumb {
                    background: #3a3f44;
                    border-radius: 4px;
                }
                
                .chat-messages::-webkit-scrollbar-thumb:hover,
                .cart-items::-webkit-scrollbar-thumb:hover {
                    background: #4a5056;
                }
            """)
        ),
        Body(
            Div(
                # Main chat area
                Div(
                    Div(
                        Div(
                            Div("🛍️", cls="logo"),
                            Div(
                                Div("AI Shopping Assistant", cls="chat-title"),
                                Div("Ask for anything you need", cls="chat-subtitle"),
                                cls="header-info"
                            ),
                            cls="header-left"
                        ),
                        Div("Beta", cls="header-badge"),
                        cls="chat-header"
                    ),
                    Div(
                        id="chat-messages",
                        cls="chat-messages",
                        hx_get="/messages",
                        hx_trigger="load",
                        hx_swap="innerHTML"
                    ),
                    Div(
                        Form(
                            Div(
                                Input(
                                    type="text",
                                    name="message",
                                    placeholder="Ask for any product you need...",
                                    autocomplete="off",
                                    id="message-input",
                                    cls="chat-input"
                                ),
                                Button(
                                    Span("↑", id="send-icon"),
                                    Div(
                                        Div(cls="loading-dot"),
                                        Div(cls="loading-dot"),
                                        Div(cls="loading-dot"),
                                        cls="loading-dots",
                                        id="loading-dots"
                                    ),
                                    type="submit",
                                    cls="send-button",
                                    id="send-button"
                                ),
                                cls="input-wrapper",
                                id="input-wrapper"
                            ),
                            hx_post="/send",
                            hx_target="#chat-messages",
                            hx_swap="innerHTML",
                            hx_indicator="#loading-indicator",
                            **{
                                "hx-on::before-request": """
                                    const input = document.getElementById('message-input');
                                    const wrapper = document.getElementById('input-wrapper');
                                    const sendBtn = document.getElementById('send-button');
                                    const sendIcon = document.getElementById('send-icon');
                                    const loadingDots = document.getElementById('loading-dots');
                                    const chatMessages = document.getElementById('chat-messages');
                                    
                                    if (!input.value.trim()) {
                                        event.preventDefault();
                                        return false;
                                    }
                                    
                                    // Disable input
                                    input.disabled = true;
                                    sendBtn.disabled = true;
                                    wrapper.classList.add('loading');
                                    
                                    // Show loading animation
                                    sendIcon.style.display = 'none';
                                    loadingDots.classList.add('active');
                                    
                                    // Clear welcome screen if it exists
                                    const welcomeMsg = chatMessages.querySelector('.welcome-message');
                                    if (welcomeMsg) {
                                        chatMessages.innerHTML = '';
                                    }
                                    
                                    // Add user message immediately
                                    const userMsg = document.createElement('div');
                                    userMsg.className = 'message-wrapper user';
                                    userMsg.style.animation = 'fadeIn 0.3s';
                                    userMsg.innerHTML = `
                                        <div class="avatar user">U</div>
                                        <div class="message-content">
                                            <div class="message-text">${input.value}</div>
                                        </div>
                                    `;
                                    chatMessages.appendChild(userMsg);
                                    
                                    // Show typing indicator
                                    const typingIndicator = document.createElement('div');
                                    typingIndicator.id = 'typing-indicator';
                                    typingIndicator.className = 'typing-indicator';
                                    typingIndicator.innerHTML = `
                                        <div class="avatar bot">AI</div>
                                        <div class="message-content">
                                            <div class="message-text">
                                                <div class="typing-dot"></div>
                                                <div class="typing-dot"></div>
                                                <div class="typing-dot"></div>
                                            </div>
                                        </div>
                                    `;
                                    chatMessages.appendChild(typingIndicator);
                                    chatMessages.scrollTop = chatMessages.scrollHeight;
                                """,
                                "hx-on::after-request": """
                                    const input = document.getElementById('message-input');
                                    const wrapper = document.getElementById('input-wrapper');
                                    const sendBtn = document.getElementById('send-button');
                                    const sendIcon = document.getElementById('send-icon');
                                    const loadingDots = document.getElementById('loading-dots');
                                    const chatMessages = document.getElementById('chat-messages');
                                    
                                    // Re-enable input
                                    input.disabled = false;
                                    sendBtn.disabled = false;
                                    wrapper.classList.remove('loading');
                                    input.value = '';
                                    
                                    // Hide loading animation
                                    sendIcon.style.display = 'block';
                                    loadingDots.classList.remove('active');
                                    
                                    // Scroll to bottom
                                    chatMessages.scrollTop = chatMessages.scrollHeight;
                                    
                                    // Focus input
                                    input.focus();
                                """
                            }
                        ),
                        cls="chat-input-container"
                    ),
                    cls="main-content"
                ),
                # Right cart sidebar
                Div(
                    Div(
                        Div("🛒 Your Cart", cls="cart-title"),
                        Div(id="cart-count", cls="cart-count"),
                        cls="cart-header"
                    ),
                    Div(
                        Div(
                            Div("🛍️", cls="cart-empty-icon"),
                            "Your cart is empty\n\nStart shopping by asking for products!",
                            cls="cart-empty"
                        ),
                        id="cart-items",
                        cls="cart-items"
                    ),
                    Div(
                        Div(
                            Div("Total", cls="total-label"),
                            Div("$0.00", id="total-amount", cls="total-amount"),
                            cls="cart-total"
                        ),
                        Button("Checkout", cls="checkout-button"),
                        id="cart-footer",
                        cls="cart-footer",
                        style="display: none;"
                    ),
                    cls="cart-sidebar"
                ),
                cls="main-wrapper"
            ),
            Script(src="https://unpkg.com/htmx.org@1.9.10")
        )
    )
    
    # Set cookie using FastHTML's built-in response handling
    from fasthtml.common import cookie
    return response, cookie("session_id", session_id, max_age=86400*30)

@rt("/messages")
def get(request: Request):
    """Get all messages"""
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    messages = session_data['messages']
    
    if not messages:
        return Div(
            Div("🛍️", cls="welcome-icon"),
            Div("Welcome to AI Shopping Assistant", cls="welcome-title"),
            Div("I can help you find and add any products to your cart. Just tell me what you need!", cls="welcome-text"),
            Div(
                Div(
                    Div("🥗", cls="prompt-icon"),
                    Div("Add groceries to my cart", cls="prompt-text"),
                    cls="prompt-card"
                ),
                Div(
                    Div("💻", cls="prompt-icon"),
                    Div("I need some electronics", cls="prompt-text"),
                    cls="prompt-card"
                ),
                Div(
                    Div("🏠", cls="prompt-icon"),
                    Div("Show me home essentials", cls="prompt-text"),
                    cls="prompt-card"
                ),
                Div(
                    Div("👕", cls="prompt-icon"),
                    Div("Add clothing items", cls="prompt-text"),
                    cls="prompt-card"
                ),
                cls="quick-prompts"
            ),
            cls="welcome-message"
        )
    
    result = []
    for msg in messages:
        result.append(ChatMessage(msg['text'], is_user=msg['is_user']))
    return result

@rt("/send")
async def post(request: Request, message: str):
    """Handle message submission"""
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    messages = session_data['messages']
    agent_message_history = session_data['agent_message_history']
    cart = session_data['cart']
    
    bot_response = ""
    
    if message.strip():
        messages.append({"text": message, "is_user": True})
        
        # Check for clear command
        if message.lower().strip() in ["clear", "clear chat", "reset"]:
            messages.clear()
            session_data['agent_message_history'] = []
            bot_response = "Chat cleared! How can I help you?"
            messages.append({"text": bot_response, "is_user": False})
        else:
            # Use Pydantic agent for response
            try:
                result = await run_agent_with_logging(message, agent_message_history)
                bot_response = result.output
                
                # Get the new messages from this interaction only
                new_messages = result.new_messages()
                
                # Process tool calls for cart actions (only from new messages)
                import json
                for msg in new_messages:
                    if hasattr(msg, 'parts'):
                        for part in msg.parts:
                            if part.__class__.__name__ == 'ToolReturnPart':
                                try:
                                    cart_action = json.loads(part.content)
                                    action = cart_action.get('action')
                                    product_name = cart_action.get('product')
                                    quantity = cart_action.get('quantity', 1)
                                    price = cart_action.get('price', 0)
                                    emoji = cart_action.get('emoji', '📦')
                                    
                                    if action == 'add':
                                        if product_name in cart:
                                            cart[product_name]['quantity'] += quantity
                                        else:
                                            cart[product_name] = {
                                                'quantity': quantity,
                                                'price': price,
                                                'emoji': emoji
                                            }
                                    elif action == 'remove':
                                        cart.pop(product_name, None)
                                    elif action == 'update':
                                        if quantity > 0:
                                            if product_name in cart:
                                                cart[product_name]['quantity'] = quantity
                                            else:
                                                cart[product_name] = {
                                                    'quantity': quantity,
                                                    'price': price,
                                                    'emoji': emoji
                                                }
                                        else:
                                            cart.pop(product_name, None)
                                except (json.JSONDecodeError, AttributeError, KeyError):
                                    pass
                
                # Update message history with all messages
                session_data['agent_message_history'] = result.all_messages()
                
                messages.append({"text": bot_response, "is_user": False})
            except Exception as e:
                bot_response = f"Sorry, I encountered an error: {str(e)}"
                messages.append({"text": bot_response, "is_user": False})
    
    # Return user message and bot response
    result = [
        ChatMessage(message, is_user=True),
        ChatMessage(bot_response, is_user=False)
    ]
    
    # Add OOB cart update
    cart_div = Div(*get_cart_items(cart), id="cart-items", **{"hx-swap-oob": "innerHTML"})
    result.append(cart_div)
    
    return result

@rt("/cart/increase/{name}")
def post(request: Request, name: str):
    """Increase cart item quantity"""
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    cart = session_data['cart']
    
    if name in cart:
        cart[name]['quantity'] += 1
    return get_cart_items(cart)

@rt("/cart/decrease/{name}")
def post(request: Request, name: str):
    """Decrease cart item quantity"""
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    cart = session_data['cart']
    
    if name in cart:
        cart[name]['quantity'] -= 1
        if cart[name]['quantity'] <= 0:
            del cart[name]
    return get_cart_items(cart)

def get_cart_items(cart):
    """Generate cart items HTML"""
    if not cart:
        return [
            Div(
                Div("🛍️", cls="cart-empty-icon"),
                "Your cart is empty\n\nStart shopping by asking for products!",
                cls="cart-empty"
            )
        ]
    
    items = []
    total = 0.0
    item_count = 0
    
    for name, item_data in cart.items():
        qty = item_data['quantity']
        price = item_data['price']
        emoji = item_data['emoji']
        items.append(CartItem(name, price, emoji, qty))
        total += price * qty
        item_count += qty
    
    # Add cart count update (OOB)
    count_text = f"{item_count} item{'s' if item_count != 1 else ''}"
    items.append(Div(count_text, id="cart-count", cls="cart-count", **{"hx-swap-oob": "innerHTML"}))
    
    # Add total amount update (OOB)
    items.append(Div(f"${total:.2f}", id="total-amount", cls="total-amount", **{"hx-swap-oob": "innerHTML"}))
    
    # Show footer (OOB)
    items.append(Div(id="cart-footer", style="display: block;", **{"hx-swap-oob": "outerHTML"}))
    
    return items

serve()