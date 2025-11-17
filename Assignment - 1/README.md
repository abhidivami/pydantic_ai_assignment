# Assignment 1 - Pydantic AI Agents

This assignment contains two AI-powered applications built using Pydantic AI and Gemini 2.5 Flash model.

## 🛍️ E-Commerce Shopping Assistant (`ecommerce_ui.py`)

An interactive shopping assistant with a ChatGPT-style interface that helps users shop for products.

### Features
- **Natural Language Shopping**: Ask for any product using natural language
- **Smart Cart Management**: Add, update, or remove items with simple commands
- **Custom Products**: Request any item, even if not in the predefined catalog
- **Quantity Updates**: Change quantities with commands like "update apple to 3"
- **Persistent Sessions**: Cart and chat history preserved across page refreshes (30-day cookie)
- **Real-time Updates**: Live cart updates with running totals
- **Modern UI**: Dark-themed, responsive interface inspired by ChatGPT
- **Input Locking**: Prevents duplicate submissions while AI is processing
- **Typing Indicators**: Visual feedback during AI response generation

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
- **HTMX**: Dynamic UI updates without page reloads

---

## 🔍 Research Agent (`task1.py`)

A research assistant that searches the web using DuckDuckGo and provides structured summaries with key facts and source citations.

### Features
- **Web Search Integration**: Uses DuckDuckGo to find relevant information
- **Structured Output**: Returns summary, key facts, and source URLs
- **Source Citations**: Provides URLs for all information sources
- **Conversational Interface**: Command-line interface for queries
- **Top 5 Results**: Searches and analyzes the top 5 web results

### How to Run
```bash
python task1.py
```
Type your research questions and the agent will search and provide structured results.

### Example Queries
- "What is the latest news about AI?"
- "Tell me about climate change effects"
- "How does photosynthesis work?"
- "What are the benefits of exercise?"

### Output Format
```
Research Output:
summary: <Concise summary of findings>
key_facts: [
  "Fact 1",
  "Fact 2",
  "Fact 3"
]
sources: [
  "URL 1",
  "URL 2",
  "URL 3"
]
```

### Tech Stack
- **Pydantic AI**: Agent framework with structured outputs
- **DuckDuckGo Search (ddgs)**: Web search API
- **Gemini 2.5 Flash**: LLM for processing and summarization
- **Pydantic**: Data validation and schema definition
- **Logfire**: Logging and monitoring

---

## 📋 Core Components

### `task2.py`
Shopping agent logic containing:
- `manage_cart()` tool: Handles add, remove, and update operations
- Product catalog with predefined items
- Custom item support with price estimation
- Agent configuration with detailed system prompts
- Message history management
- Logfire integration for debugging

### `ecommerce_ui.py`
Web interface implementation:
- FastHTML-based web server
- Session management with UUID-based cookies
- HTMX integration for dynamic updates
- ChatGPT-inspired UI with dark theme
- Cart sidebar with real-time totals
- Welcome screen with quick prompts
- Responsive design with animations

### `task1.py`
Research agent implementation:
- DuckDuckGo search tool integration
- Structured output using Pydantic models
- Command-line interface
- Top 5 result processing and summarization

---

## 🛠️ Setup Requirements

### Install Dependencies
```bash
pip install pydantic-ai
pip install python-fasthtml
pip install logfire
pip install duckduckgo-search
pip install python-dotenv
```

### Environment Variables
Create a `.env` file in the Assignment - 1 folder:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your API key from: [Google AI Studio](https://aistudio.google.com/apikey)

---

## 🎯 Key Concepts Demonstrated

1. **Tool Calling**: Agents use defined tools (`web_search`, `manage_cart`) to perform actions
2. **Conversational Context**: Message history maintained for context-aware responses
3. **Session Management**: User-specific data persistence using cookies
4. **Real-time UI Updates**: HTMX for dynamic, seamless updates
5. **Structured Output**: Type-safe responses using Pydantic models (`ResearchOutput`)
6. **Error Handling**: Graceful handling of API errors and edge cases
7. **Custom Item Support**: Dynamic product addition with price estimation
8. **State Management**: Per-session cart and message storage

---

## 📝 Important Notes

### E-Commerce App
- Uses in-memory session storage (data resets on server restart)
- Sessions expire after 30 days or when cookies are cleared
- Each browser/user gets a unique session ID
- Cart items persist across page refreshes
- Input is disabled during AI processing to prevent duplicates

### Research Agent
- Requires internet connection for web searches
- Returns top 5 DuckDuckGo search results
- Output follows structured Pydantic schema
- Type `exit` to quit the application

### General
- All AI interactions are logged to Logfire for monitoring
- UI is optimized for desktop browsers (responsive design)
- Gemini 2.5 Flash model is used for both applications

---

## 🚀 Future Enhancements

### E-Commerce
- Database persistence (PostgreSQL/SQLite)
- User authentication and profiles
- Payment gateway integration
- Order history and tracking
- Product recommendations using embeddings
- Multi-language support

### Research Agent
- PDF/Document analysis
- Academic paper search integration
- Fact-checking with multiple sources
- Export results to markdown/PDF
- Citation formatting (APA, MLA, etc.)

---

## 📚 Project Structure

```
Assignment - 1/
├── ecommerce_ui.py      # Web-based shopping assistant UI
├── task2.py             # Shopping agent core logic and tools
├── task1.py             # Research agent with web search
├── README.md            # This file
├── .env                 # Environment variables (API keys)
└── .logfire/            # Logfire logs and configuration
```

---

## 🐛 Troubleshooting

**Issue**: "No module named 'pydantic_ai'"
- **Solution**: Run `pip install pydantic-ai`

**Issue**: Raw HTML showing instead of rendered page
- **Solution**: Ensure FastHTML is properly installed and you're using the latest version

**Issue**: Session not persisting
- **Solution**: Check if cookies are enabled in your browser

**Issue**: Research agent not finding results
- **Solution**: Check internet connection and DuckDuckGo accessibility

**Issue**: API key error
- **Solution**: Verify `.env` file exists with correct `GOOGLE_API_KEY`
