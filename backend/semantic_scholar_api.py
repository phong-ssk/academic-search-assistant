"""
Backend API cho Semantic Scholar Search
"""
import requests
from typing import List, Dict, Optional
import time

class SemanticScholarAPI:
    """Class xử lý tìm kiếm Semantic Scholar"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

    def search(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Tìm kiếm Semantic Scholar
        """
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,authors,venue,year,abstract,externalIds,url,citationCount"
        }
        
        if year_start and year_end:
            params["year"] = f"{year_start}-{year_end}"
        elif year_start:
            params["year"] = f"{year_start}-"

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 429:
                print("Semantic Scholar Rate Limit Hit. Waiting...")
                time.sleep(2)
                response = requests.get(self.base_url, headers=self.headers, params=params)

            response.raise_for_status()
            data = response.json()
            
            return self._parse_data(data.get("data", []))
        except Exception as e:
            print(f"Semantic Scholar search error: {e}")
            return []

    def _parse_data(self, papers: List[Dict]) -> List[Dict]:
        """
        Parse danh sách kết quả
        """
        results = []
        for paper in papers:
            try:
                paper_id = paper.get("paperId", "N/A")
                title = paper.get("title", "N/A")
                
                authors = [author.get("name") for author in paper.get("authors", [])]
                
                venue = paper.get("venue", "N/A")
                year = paper.get("year", "N/A")
                abstract = paper.get("abstract", "N/A")
                link = paper.get("url", f"https://www.semanticscholar.org/paper/{paper_id}")
                
                external_ids = paper.get("externalIds", {})
                doi = external_ids.get("DOI", "N/A")
                cited_by = paper.get("citationCount", 0)

                results.append({
                    "id": paper_id,
                    "title": title,
                    "authors": authors,
                    "journal": venue,
                    "year": year,
                    "doi": doi,
                    "abstract": abstract,
                    "link": link,
                    "cited_by": cited_by,
                    "source": "Semantic Scholar"
                })
            except Exception as e:
                print(f"Error parsing Semantic Scholar paper: {e}")
                continue
                
        return results

    def search_and_fetch(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Tìm kiếm và trả về kết quả
        """
        return self.search(query, max_results, year_start, year_end)
