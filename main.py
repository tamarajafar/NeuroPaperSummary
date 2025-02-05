import streamlit as st
import feedparser
import openai
import smtplib
import schedule
import time
import firebase_admin
from firebase_admin import credentials, firestore
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 🔗 Firebase for storing subscribers & engagement
cred = credentials.Certificate("firebase_creds.json")  # Ensure your Firebase credentials file is set
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🌍 RSS Feeds for Biotech & VC news
RSS_FEEDS = [
    "https://www.fiercebiotech.com/rss.xml",
    "https://www.statnews.com/feed/",
    "https://techcrunch.com/category/biotech/feed/",
    "https://news.crunchbase.com/feed/"
]

# 🧠 GPT-4 Summarization Function
def summarize_news(news_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Summarize this biotech news in 3 sentences."},
                  {"role": "user", "content": news_text}]
    )
    return response['choices'][0]['message']['content']

# 🔍 Fetch News from RSS and Summarize
def fetch_and_summarize_news():
    news_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Top 3 news per source
            summary = summarize_news(entry.summary)
            news_items.append(f"<li><a href='{entry.link}' target='_blank'>{entry.title}</a>: {summary}</li>")
    return "<ul>" + "".join(news_items) + "</ul>"

# ✉️ Generate HTML Newsletter
def generate_newsletter():
    news_content = fetch_and_summarize_news()
    newsletter_html = f"""
    <html>
        <body>
            <h2>Weekly Biotech & VC Insights</h2>
            {news_content}
            <p>Stay ahead in biotech and venture capital!</p>
        </body>
    </html>
    """
    return newsletter_html

# 📬 Send Newsletter via SMTP
def send_email(newsletter_html, recipient_email):
    sender_email = "your_email@example.com"
    password = "your_email_password"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Weekly Biotech & VC Newsletter"
    msg.attach(MIMEText(newsletter_html, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return "Newsletter sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

# 📌 Streamlit UI
st.title("📩 Biotech & VC Weekly Newsletter")
st.markdown("**Built by Tamara Jafar** ([LinkedIn](https://www.linkedin.com/in/tamarajafar/) | [X](https://x.com/TamaraJafar))")

st.subheader("🔍 Preview This Week's Newsletter")
st.markdown(generate_newsletter(), unsafe_allow_html=True)

st.subheader("📬 Send Newsletter")
recipient_email = st.text_input("Enter recipient email:")
if st.button("Send Now"):
    if recipient_email:
        result = send_email(generate_newsletter(), recipient_email)
        st.success(result)
    else:
        st.error("Please enter a valid email address.")

# ✅ Track Subscribers in Firebase
st.subheader("📨 Subscribe to Weekly Newsletter")
new_subscriber = st.text_input("Enter your email to subscribe:")
if st.button("Subscribe"):
    if new_subscriber:
        db.collection("subscribers").add({"email": new_subscriber})
        st.success("You're subscribed!")
    else:
        st.error("Please enter a valid email address.")
