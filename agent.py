import os
import time
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file!")

client = Groq(api_key=api_key)

TOPICS = [
    "latest AI news 2026",
    "Pakistan economy news 2026",
    "cricket latest news 2026",
    "cryptocurrency prices 2026",
    "technology trends 2026"
]

DELAY_BETWEEN_TOPICS = 3


def divider():
    print("-" * 60)


def search(topic):
    print(f"  searching: {topic}")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(topic, max_results=5):
                results.append(r["body"])
    except Exception:
        print(f"  search failed, retrying...")
        time.sleep(5)
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(topic, max_results=3):
                    results.append(r["body"])
        except Exception:
            print(f"  skipping '{topic}', couldn't reach search.\n")
            return ""
    return "\n\n".join(results)


def make_pdf(topic, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_topic = (
        topic[:30]
        .replace(" ", "_")
        .replace("?", "")
        .replace("!", "")
        .replace(":", "")
        .replace("/", "")
        .replace("\\", "")
    )
    filename = f"{safe_topic}_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=22,
        textColor=HexColor("#2C3E50"),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        "meta",
        parent=styles["Normal"],
        fontSize=11,
        textColor=HexColor("#7F8C8D"),
        spaceAfter=16
    )
    heading_style = ParagraphStyle(
        "heading",
        parent=styles["Normal"],
        fontSize=13,
        textColor=HexColor("#2980B9"),
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=11,
        textColor=HexColor("#2C3E50"),
        spaceAfter=10,
        leading=17
    )

    page = []
    page.append(Paragraph("AI Research Report", title_style))
    page.append(Paragraph(f"Topic: {topic}", meta_style))
    page.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y %H:%M')}", meta_style))
    page.append(Spacer(1, 0.2 * inch))
    page.append(Paragraph("Summary", heading_style))
    page.append(Spacer(1, 0.1 * inch))

    for line in summary.split("\n"):
        if line.strip():
            page.append(Paragraph(line.strip(), body_style))

    page.append(Spacer(1, 0.4 * inch))
    page.append(Paragraph("By Abdul Wasay", meta_style))

    doc.build(page)
    return filename


def research(topic):
    history = [
        {
            "role": "system",
            "content": "You are a research assistant. Summarize the search results below into a clean, readable report. No bullet points with stars, just plain text paragraphs."
        }
    ]

    raw = search(topic)
    if not raw:
        return

    history.append({
        "role": "user",
        "content": f"Search results for '{topic}':\n\n{raw}\n\nWrite a clear summary."
    })

    print(f"  summarizing...")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        max_tokens=700
    )

    summary = response.choices[0].message.content.replace("**", "")

    divider()
    print(f"  {topic.upper()}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    divider()
    print(f"\n{summary}\n")
    divider()

    pdf = make_pdf(topic, summary)
    print(f"  saved: {pdf}\n")


def run():
    print("\nAI Research Agent")
    print("by Abdul Wasay\n")
    divider()

    for i, topic in enumerate(TOPICS, 1):
        print(f"\n[{i}/{len(TOPICS)}] {topic}")
        research(topic)

        if i < len(TOPICS):
            time.sleep(DELAY_BETWEEN_TOPICS)

    divider()
    print(f"\nDone. {len(TOPICS)} reports saved.\n")


run()