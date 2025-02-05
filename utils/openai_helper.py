import os
from openai import OpenAI
import json

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

class ResearchSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def summarize_paper(self, title, abstract):
        try:
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
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Failed to summarize paper: {e}")
