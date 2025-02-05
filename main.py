import os
import streamlit as st
import feedparser
import openai
import smtplib
import schedule
import firebase_admin
from firebase_admin import credentials, firestore
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 🔹 Force install dependencies (fixes missing modules issue)
os.system("pip install -r requirements.txt")

# 🔹 Load API Keys securely from Streamlit Secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME") or st.secrets["EMAIL_USERNAME"]
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or st.secrets["EMAIL_PASSWORD"]


# ✅ Ensure Firebase credentials exist
if "firebase" in st.secrets:
    try:
        # Convert JSON string to Python dictionary
        firebase_creds = json.loads(st.secrets["firebase"]["credentials"])
        
        # Initialize Firebase
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        st.success("✅ Firebase Initialized Successfully!")
    except Exception as e:
        st.error(f"🚨 Firebase Initialization Failed: {e}")
else:
    st.error("🚨 Firebase credentials are missing! Add them to Streamlit Secrets.")

# 🌍 RSS Feeds for Biotech & VC news
RSS_FEEDS = [
    "https://www.fiercebiotech.com/rss.xml",
    "https://www.statnews.com/feed/",
    "https://techcrunch.com/category/biotech/feed/",
    "https://news.crunchbase.com/feed/"
]

# 🧠 GPT-4 Summarization Function
def summarize_news(news_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            api_key=OPENAI_API_KEY,  # 🔹 Ensuring API key is used correctly
            messages=[{"role": "system", "content": "Summarize this biotech news in 3 sentences."},
                      {"role": "user", "content": news_text}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error summarizing: {e}"

# 🔍 Fetch News from RSS and Summarize
def fetch_and_summarize_news():
    news_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Top 3 news per source
            summary = summarize_news(entry.summary if "summary" in entry else entry.title)
            news_items.append(f"<li><a href='{entry.link}' target='_blank'>{entry.title}</a>: {summary}</li>")
    return "<ul>" + "".join(news_items) + "</ul>"

# ✉️ Generate HTML Newsletter
def generate_newsletter():
    news_content = fetch_and_summarize_news()
    return f"""
    <html>
        <body>
            <h2>Weekly Biotech & VC Insights</h2>
            {news_content}
            <p>Stay ahead in biotech and venture capital!</p>
        </body>
    </html>
    """

# 📬 Send Newsletter via SMTP (Consider Using Mailchimp Instead)
def send_email(newsletter_html, recipient_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = recipient_email
    msg['Subject'] = "Weekly Biotech & VC Newsletter"
    msg.attach(MIMEText(newsletter_html, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, recipient_email, msg.as_string())
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

# ✅ Ensure Streamlit runs properly
if __name__ == "__main__":
    st.write("App Running Successfully 🚀")
