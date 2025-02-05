import streamlit as st
import json
from datetime import datetime, timedelta
import streamlit_calendar as st_cal
from utils.openai_helper import ResearchSummarizer
from utils.paper_processor import PaperFetcher
import markdown

# Page configuration
st.set_page_config(
    page_title="Academic Profile",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease-in-out;
    }

    .block-container {
        padding: 3rem 2rem !important;
        max-width: 1200px;
        margin: 0 auto;
    }

    .main > div {
        padding: 2.5rem;
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .main > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.08);
    }

    h1 {
        color: #1e3d59;
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        letter-spacing: -0.02em;
        line-height: 1.2 !important;
    }

    h2 {
        color: #2a4a6d;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin: 1.8rem 0 1.2rem !important;
        letter-spacing: -0.01em;
    }

    h3 {
        color: #355a82;
        font-size: 1.6rem !important;
        font-weight: 500 !important;
        margin: 1.5rem 0 1rem !important;
    }

    p, li {
        color: #4a5568;
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
        margin-bottom: 1rem !important;
    }

    a {
        color: #2b6cb0;
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.2s ease;
    }

    a:hover {
        border-color: #2b6cb0;
    }

    .stButton > button {
        width: 100%;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #1e3d59 0%, #2a4a6d 100%);
        color: white;
        font-weight: 500;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 2px 10px rgba(30, 61, 89, 0.15);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(30, 61, 89, 0.25);
    }

    .sidebar .sidebar-content {
        background: #f8fafc;
        padding: 2rem 1rem;
    }

    .stSelectbox > div > div {
        background-color: white;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
    }

    .stSelectbox > div > div:hover {
        border-color: #2b6cb0;
    }

    /* Publications cards */
    .publication-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }

    .publication-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)
""", unsafe_allow_html=True)

# Initialize session state
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "About"

# Sidebar navigation
st.sidebar.title("Navigation")
st.session_state.current_tab = st.sidebar.radio(
    "Go to",
    ["About", "CV", "Publications", "Book Meeting", "Research Summarizer"]
)

def load_markdown_content(file_path):
    with open(file_path, 'r') as file:
        return markdown.markdown(file.read())

def load_json_content(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# About Me Section
if st.session_state.current_tab == "About":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("assets/profile.svg", width=250)
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <a href='mailto:researcher@institution.edu' style='text-decoration: none; color: #1e3d59;'>
                    <i class='fas fa-envelope'></i> Email
                </a> &nbsp;|&nbsp;
                <a href='https://linkedin.com' style='text-decoration: none; color: #1e3d59;'>
                    <i class='fab fa-linkedin'></i> LinkedIn
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.title("About Me")
        about_content = load_markdown_content("data/about.md")
        st.markdown(about_content, unsafe_allow_html=True)

# CV Section
elif st.session_state.current_tab == "CV":
    st.title("Curriculum Vitae")
    cv_content = load_markdown_content("data/cv.md")
    st.markdown(cv_content, unsafe_allow_html=True)
    
    # Download CV button
    st.download_button(
        label="Download CV as PDF",
        data=cv_content,
        file_name="cv.pdf",
        mime="application/pdf"
    )

# Publications Section
elif st.session_state.current_tab == "Publications":
    st.title("Publications")
    publications = load_json_content("data/publications.json")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        year_filter = st.selectbox(
            "Filter by Year",
            ["All"] + sorted(list(set(pub["year"] for pub in publications)), reverse=True),
            index=0
        )
    with col2:
        type_filter = st.selectbox(
            "Publication Type",
            ["All", "Journal", "Conference", "Book Chapter"],
            index=0
        )
    
    # Display filtered publications
    for pub in publications:
        if year_filter == "All" or pub["year"] == year_filter:
            st.markdown(f"""
            ### {pub['title']}
            **Authors:** {pub['authors']}  
            **Year:** {pub['year']}  
            **Journal:** {pub['journal']}  
            [Link to paper]({pub['url']})
            """)
            st.divider()

# Book Meeting Section
elif st.session_state.current_tab == "Book Meeting":
    st.title("Schedule a Meeting")
    
    # Calendar setup
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "initialView": "timeGridWeek",
        "selectable": True,
        "selectMirror": True,
        "weekends": False,
    }
    
    # Create available time slots
    events = []
    start_date = datetime.now()
    for i in range(14):  # Next 2 weeks
        current_date = start_date + timedelta(days=i)
        if current_date.weekday() < 5:  # Monday to Friday
            events.append({
                "title": "Available",
                "start": (current_date + timedelta(hours=9)).isoformat(),
                "end": (current_date + timedelta(hours=17)).isoformat(),
                "color": "#28a745"
            })
    
    calendar = st_cal.calendar(events=events, options=calendar_options)
    
    if calendar.get("eventClick"):
        st.success("Meeting request sent! You will receive a confirmation email shortly.")

# Research Summarizer Section
elif st.session_state.current_tab == "Research Summarizer":
    st.title("AI-Powered Research Summarizer")
    
    search_query = st.text_input("Enter your research topic:")
    
    if search_query:
        try:
            with st.spinner("Fetching and analyzing papers..."):
                paper_fetcher = PaperFetcher()
                summarizer = ResearchSummarizer()
                
                papers = paper_fetcher.search_papers(search_query)
                
                for paper in papers:
                    st.markdown(f"### {paper['title']}")
                    
                    summary = summarizer.summarize_paper(paper['title'], paper['abstract'])
                    
                    with st.expander("View Summary"):
                        st.markdown("**Key Findings:**")
                        st.write(summary['key_findings'])
                        st.markdown("**Methodology:**")
                        st.write(summary['methodology'])
                        st.markdown("**Implications:**")
                        st.write(summary['implications'])
                        
                    st.divider()
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
