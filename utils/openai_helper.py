import os
from openai import OpenAI
import json
from .database import get_db, get_paper_by_title, save_summary

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

class ResearchSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.db = next(get_db())

    def summarize_paper(self, title, abstract):
        try:
            # Check if we already have a summary in the database
            paper = get_paper_by_title(self.db, title)
            if paper and paper.summary:
                return {
                    "key_findings": paper.summary.key_findings,
                    "methodology": paper.summary.methodology,
                    "implications": paper.summary.implications
                }

            # If not in database, generate new summary
            prompt = f"""Analyze and summarize the following research paper:
            Title: {title}
            Abstract: {abstract}

            Provide a response in the following JSON format:
            {{
                "key_findings": string,
                "methodology": string,
                "implications": string
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            summary_data = json.loads(response.choices[0].message.content)

            # Save summary to database if paper exists
            if paper:
                save_summary(self.db, paper.id, summary_data)

            return summary_data
        except Exception as e:
            raise Exception(f"Failed to summarize paper: {e}")