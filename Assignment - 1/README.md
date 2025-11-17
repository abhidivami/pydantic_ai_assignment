# Assignment 1 - Pydantic AI Agents

This assignment contains two AI-powered applications built using Pydantic AI and Gemini 2.5 Flash model.

## 🛍️ E-Commerce Shopping Assistant (`ecommerce_ui.py`)

An interactive shopping assistant with a ChatGPT-style interface that helps users shop for products.

### Features
- **Natural Language Shopping**: Ask for any product using natural language
- **Smart Cart Management**: Add, update, or remove items with simple commands
- **Custom Products**: Request any item, even if not in the predefined catalog
- **Quantity Updates**: Change quantities with commands like "update apple to 3"
- **Persistent Sessions**: Cart and chat history preserved across page refreshes
- **Real-time Updates**: Live cart updates with running totals
- **Modern UI**: Dark-themed, responsive interface inspired by ChatGPT

### How to Run
```bash
python ecommerce_ui.py
```
Then open your browser to the URL shown in the terminal (usually `http://localhost:5001`)

### Example Commands
- "Add 2 apples to my cart"
- "I need some salt and pepper"
- "Update the quantity of banana to 5"
- "Remove toothpaste from cart"
- "Add a laptop" (custom item with estimated pricing)

### Tech Stack
- **Pydantic AI**: Agent framework with tool calling
- **FastHTML**: Modern Python web framework
- **Gemini 2.5 Flash**: Google's LLM for natural language understanding
- **Logfire**: Observability and logging

---

## 🔍 Research Agent (`task1.py`)

A research assistant that searches the web using DuckDuckGo and provides summarized answers with source citations.

### Features
- **Web Search Integration**: Uses DuckDuckGo to find relevant information
- **Source Citations**: Provides URLs for all information sources
- **Structured Results**: Returns title, snippet, and URL for each source
- **Conversational Interface**: Natural language queries and responses

### How to Run
```bash
python duckduckgo_tool.py
```
Type your questions and the agent will search and summarize results for you.

### Example Queries
- "What is the latest news about AI?"
- "Tell me about climate change effects"
- "How does photosynthesis work?"

### Tech Stack
- **Pydantic AI**: Agent framework
- **DuckDuckGo API**: Web search functionality
- **Gemini 2.5 Flash**: LLM for processing and summarization
- **Logfire**: Logging and monitoring

---

## 📋 Common Components

### `task2.py`
Core shopping agent logic with:
- Cart management tools (add, remove, update)
- Product pricing logic
- Custom item support
- Agent configuration and system prompts

### Setup Requirements
```bash
pip install pydantic-ai
pip install python-fasthtml
pip install logfire
pip install duckduckgo-search
pip install python-dotenv
```

### Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

---

## 🎯 Key Concepts Demonstrated

1. **Tool Calling**: Agents use defined tools to perform actions (search, cart management)
2. **Conversational Context**: Message history maintained for context-aware responses
3. **Session Management**: User-specific data persistence
4. **Real-time UI Updates**: HTMX for dynamic, no-reload updates
5. **Structured Output**: Type-safe responses using Pydantic models
6. **Error Handling**: Graceful handling of API errors and edge cases

---

## 📝 Notes

- The e-commerce app uses in-memory session storage (resets on server restart)
- Sessions expire after 30 days or when cookies are cleared
- All AI responses are logged to Logfire for debugging and monitoring
- The UI is optimized for desktop browsers (responsive design)

## 🚀 Future Enhancements

- Database persistence for cart data
- User authentication
- Payment integration
- Product recommendations
- Advanced search filters
- Export chat history
