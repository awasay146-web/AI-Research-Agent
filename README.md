# AI Research Agent

A Python automation tool that researches topics from the web and saves the results as formatted PDF reports.

I built this to automate the research process — instead of manually searching and summarizing topics, this agent does it automatically.

## What it does

- Searches the web for any topic using DuckDuckGo
- Sends results to an AI model for summarization
- Saves each summary as a clean PDF report
- Runs fully automatically through a topics list

## Tech used

- Python
- Groq API (Llama 3.1)
- DuckDuckGo Search
- ReportLab

## Setup

1. Clone the repo
2. Install dependencies:
```
   pip install groq ddgs reportlab python-dotenv
```
3. Create a `.env` file:
```
   GROQ_API_KEY=your_key_here
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