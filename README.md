# AI Research Agent

A Python automation tool that researches topics from the web and saves the results as formatted PDF reports.

I built this to automate the research process — instead of manually searching and summarizing topics, this agent does it automatically.

## What it does

- Searches the web for any topic using DuckDuckGo or Tavily
- Sends results to an AI model for summarization
- Saves each summary as a clean PDF report
- Runs fully automatically through a topics list

## Tech used

- Python
- Groq API (Llama 3.1)
- DuckDuckGo Search
- Tavily Search (optional)
- ReportLab

## Setup

1. Clone the repo
2. Install dependencies:
```
   pip install groq ddgs reportlab python-dotenv tavily-python
```
3. Create a `.env` file:
```
   GROQ_API_KEY=your_key_here
   TAVILY_API_KEY=your_tavily_key_here   # optional, needed if using Tavily
   SEARCH_PROVIDER=ddgs                  # 'ddgs' (default) or 'tavily'
```
4. Edit the `TOPICS` list in `agent.py`
5. Run:
```
   python agent.py
```

## Output

Each topic generates a PDF report saved in the project folder.

---

By Abdul Wasay