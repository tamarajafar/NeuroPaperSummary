import requests
import xml.etree.ElementTree as ET
from datetime import datetime

class PaperFetcher:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
    def search_papers(self, query, max_results=10):
        try:
            # Search for paper IDs
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "sort": "date"
            }
            
            response = requests.get(search_url, params=params)
            root = ET.fromstring(response.content)
            
            # Extract paper IDs
            id_list = root.findall(".//Id")
            paper_ids = [id_elem.text for id_elem in id_list]
            
            # Fetch paper details
            if not paper_ids:
                return []
                
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(paper_ids),
                "retmode": "xml"
            }
            
            response = requests.get(fetch_url, params=params)
            root = ET.fromstring(response.content)
            
            papers = []
            for article in root.findall(".//PubmedArticle"):
                try:
                    title = article.find(".//ArticleTitle").text
                    abstract = article.find(".//Abstract/AbstractText")
                    abstract = abstract.text if abstract is not None else "No abstract available"
                    
                    papers.append({
                        "title": title,
                        "abstract": abstract
                    })
                except Exception as e:
                    continue
                    
            return papers
            
        except Exception as e:
            raise Exception(f"Failed to fetch papers: {e}")
