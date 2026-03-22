import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
from pytrends.request import TrendReq
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
email_address = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")
base_dir = os.path.dirname(os.path.abspath(__file__))

if not api_key:
    raise ValueError("GROQ_API_KEY not found!")
if not email_address:
    raise ValueError("EMAIL_ADDRESS not found!")
if not email_password:
    raise ValueError("EMAIL_PASSWORD not found!")

client = Groq(api_key=api_key)

DELAY_BETWEEN_TOPICS = 3
generated_pdfs = []


def divider():
    print("-" * 60)


def get_trending_topics():
    print("  fetching trending topics from Google Trends...\n")
    try:
        pytrends = TrendReq(hl='en-US', tz=300)
        trending = pytrends.trending_searches(pn='pakistan')
        topics = trending[0].tolist()[:10]

        print(f"  found {len(topics)} trending topics\n")
        print("  asking AI to pick best ones...\n")

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a content strategist. Pick the 5 most interesting and research-worthy topics from the list. Return only the 5 topics as a numbered list, nothing else."
                },
                {
                    "role": "user",
                    "content": f"Today's trending topics in Pakistan:\n{chr(10).join(topics)}\n\nPick the 5 most interesting ones for research."
                }
            ],
            max_tokens=200
        )

        ai_response = response.choices[0].message.content
        selected = []
        for line in ai_response.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                topic = line.split(".", 1)[-1].strip()
                if topic:
                    selected.append(topic)

        if selected:
            print(f"  AI selected: {selected}\n")
            return selected[:5]
        else:
            return topics[:5]

    except Exception as e:
        print(f"  Google Trends failed: {e}")
        print("  using fallback topics...\n")
        return [
            "latest AI news 2026",
            "Pakistan economy 2026",
            "cricket news 2026",
            "cryptocurrency 2026",
            "technology trends 2026"
        ]


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
            print(f"  skipping '{topic}'\n")
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
    filename = os.path.join(base_dir, f"{safe_topic}_{timestamp}.pdf")

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
            "content": "You are a research assistant. Summarize the search results into a clean readable report. No stars or bullet points, just plain paragraphs."
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
    generated_pdfs.append(pdf)
    print(f"  saved: {pdf}\n")


def send_email(pdf_files, topics):
    print("\n  sending email...\n")

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = email_address
    msg["Subject"] = f"Daily AI Research Reports - {datetime.now().strftime('%B %d, %Y')}"

    body = f"""
Hi Abdul Wasay,

Your daily AI research reports are ready!

Today's trending topics researched:
{chr(10).join(f"- {t}" for t in topics)}

Date: {datetime.now().strftime('%B %d, %Y %H:%M')}

Reports are attached as PDF files.

By AI Research Agent
    """

    msg.attach(MIMEText(body, "plain"))

    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(pdf_file)}"
                )
                msg.attach(part)
        except Exception as e:
            print(f"  could not attach {pdf_file}: {e}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
        print(f"  attached {len(pdf_files)} PDFs")
        print("  email sent! ✅\n")
    except Exception as e:
        print(f"  email failed: {e}\n")


def run():
    print("\nAI Research Agent")
    print("By Abdul Wasay\n")
    divider()

    topics = get_trending_topics()

    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] {topic}")
        research(topic)

        if i < len(topics):
            time.sleep(DELAY_BETWEEN_TOPICS)

    divider()
    print(f"\nDone. {len(topics)} reports saved.")

    if generated_pdfs:
        send_email(generated_pdfs, topics)

    print("\nAll done! Trending topics researched and emailed.\n")


run()