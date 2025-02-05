
import requests
from bs4 import BeautifulSoup
import openai
from datetime import datetime
import json
import os

class NewsletterGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def scrape_rss_feed(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:5]  # Get latest 5 items
        
        news_items = []
        for item in items:
            news_items.append({
                'title': item.title.text,
                'link': item.link.text,
                'description': item.description.text,
                'date': item.pubDate.text if item.pubDate else datetime.now().isoformat()
            })
        return news_items
    
    def summarize_content(self, content):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "user",
                "content": f"Summarize this biotech/VC news in 2-3 sentences: {content}"
            }],
            max_tokens=150
        )
        return response.choices[0].message.content
        
    def generate_newsletter(self):
        sources = {
            'fiercebiotech': 'https://www.fiercebiotech.com/rss/xml',
            'techcrunch': 'https://techcrunch.com/category/biotech/feed/',
            'stat': 'https://www.statnews.com/feed'
        }
        
        newsletter_content = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'sections': []
        }
        
        for source_name, url in sources.items():
            try:
                news_items = self.scrape_rss_feed(url)
                summaries = []
                for item in news_items:
                    summary = self.summarize_content(item['description'])
                    summaries.append({
                        'title': item['title'],
                        'summary': summary,
                        'link': item['link']
                    })
                
                newsletter_content['sections'].append({
                    'source': source_name,
                    'items': summaries
                })
            except Exception as e:
                print(f"Error processing {source_name}: {str(e)}")
        
        return newsletter_content
