AI Research Agent

A fully automated research pipeline: it finds what's trending, researches it, writes a report, and emails it — with zero manual steps.

I built this to remove manual research work entirely. Instead of me searching, reading, and summarizing topics by hand, the agent does all of it on its own and delivers a finished report straight to my inbox.

What it does
Fetches real-time trending topics from Google Trends (Pakistan) via RSS
Uses an LLM (Groq / Llama 3.1) to pick the 5 most research-worthy topics from that list
Searches the web for each topic using DuckDuckGo
Summarizes findings into a clean, readable report using Llama 3.1
Generates a formatted PDF for each topic using ReportLab
Emails all reports automatically as attachments via Gmail SMTP
Falls back gracefully to a default topic list if the live trends feed is unavailable, so the pipeline never breaks

Runs unattended end-to-end — no manual input required after starting it, and can be scheduled to run automatically (e.g. via Windows Task Scheduler).

Tech used
Python
Groq API (Llama 3.1) — topic selection and summarization
Google Trends RSS — live trending topic discovery
DuckDuckGo Search (ddgs) — web research
ReportLab — PDF report generation
smtplib — automated email delivery
python-dotenv — environment configuration
Setup
Clone the repo:
   git clone https://github.com/awasay146-web/AI-Research-Agent.git
   cd AI-Research-Agent
Install dependencies:
   pip install -r requirements.txt
Create a .env file in the project root (see .env.example):
   GROQ_API_KEY=your_groq_api_key
   EMAIL_ADDRESS=your_gmail_address
   EMAIL_PASSWORD=your_gmail_app_password

Note: EMAIL_PASSWORD must be a Google App Password, not your regular Gmail password.

Run it:
   python agent.py
Output

Each run generates one PDF report per selected topic, saved in the project folder, and emails all of them as attachments in a single message.