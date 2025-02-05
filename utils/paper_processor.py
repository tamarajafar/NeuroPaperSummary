import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from .database import get_db, get_paper_by_title, save_paper, save_summary

class PaperFetcher:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.db = next(get_db())

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
            paper_ids = [id_elem.text for id_elem in id_list if id_elem.text is not None]

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
                    title_elem = article.find(".//ArticleTitle")
                    if title_elem is not None and title_elem.text is not None:
                        title = title_elem.text
                        # Check if paper exists in database
                        existing_paper = get_paper_by_title(self.db, title)
                        if existing_paper:
                            papers.append({
                                "title": existing_paper.title,
                                "abstract": existing_paper.abstract,
                                "authors": existing_paper.authors,
                                "url": existing_paper.url
                            })
                            continue

                        abstract_elem = article.find(".//Abstract/AbstractText")
                        abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"

                        # Save new paper to database
                        paper_data = {
                            "title": title,
                            "abstract": abstract,
                            "authors": "Authors not implemented",  # TODO: Implement author extraction
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{article.find('.//PMID').text}/"
                        }
                        saved_paper = save_paper(self.db, paper_data)
                        papers.append(paper_data)

                except Exception as e:
                    continue

            return papers

        except Exception as e:
            raise Exception(f"Failed to fetch papers: {e}")