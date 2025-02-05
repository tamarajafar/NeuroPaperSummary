import streamlit as st
import json
from datetime import datetime, timedelta
import streamlit_calendar as st_cal
from utils.openai_helper import ResearchSummarizer
from utils.paper_processor import PaperFetcher
import markdown

# Page configuration
st.set_page_config(page_title="Academic Profile", layout="wide")

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
    st.title("About Me")
    about_content = load_markdown_content("data/about.md")
    st.markdown(about_content, unsafe_allow_html=True)
    
    # Profile image using Font Awesome
    st.markdown("""
        <i class="fas fa-user-circle fa-10x"></i>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

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
    
    # Filter options
    year_filter = st.selectbox(
        "Filter by year",
        ["All"] + sorted(list(set(pub["year"] for pub in publications))),
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
