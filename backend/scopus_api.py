"""
Backend API cho Scopus Search
"""
import requests
from typing import List, Dict, Optional

class ScopusAPI:
    """Class xử lý tìm kiếm Scopus"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elsevier.com/content/search/scopus"
        self.headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }

    def search(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Tìm kiếm Scopus và trả về danh sách bài báo
        """
        if not self.api_key:
            return []

        # Build query
        final_query = query
        if year_start and year_end:
            final_query = f"{query} AND PUBYEAR > {year_start-1} AND PUBYEAR < {year_end+1}"
        elif year_start:
            final_query = f"{query} AND PUBYEAR > {year_start-1}"

        params = {
            "query": final_query,
            "count": max_results,
            "view": "COMPLETE"  # Changed to COMPLETE to get full abstract
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            entries = data.get("search-results", {}).get("entry", [])
            return self._parse_entries(entries)
        except Exception as e:
            print(f"Scopus search error: {e}")
            return []

    def _parse_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Parse danh sách kết quả từ Scopus
        """
        results = []
        for entry in entries:
            try:
                # Extract info
                title = entry.get("dc:title", "N/A")
                
                # Get all authors, not just creator
                creator = entry.get("dc:creator", "N/A")
                authors = []
                if "author" in entry:
                    authors = [author.get("authname", "") for author in entry.get("author", [])]
                elif creator != "N/A":
                    authors = [creator]
                
                publication = entry.get("prism:publicationName", "N/A")
                cover_date = entry.get("prism:coverDate", "N/A")
                year = cover_date.split("-")[0] if cover_date != "N/A" else "N/A"
                doi = entry.get("prism:doi", "N/A")
                scopus_id = entry.get("dc:identifier", "").replace("SCOPUS_ID:", "")
                
                # Abstract from COMPLETE view
                abstract = entry.get("dc:description", "N/A")
                
                # Citation count
                cited_by_count = entry.get("citedby-count", "0")
                
                link = next((link['@href'] for link in entry.get('link', []) if link.get('@ref') == 'scopus'), "N/A")

                results.append({
                    "id": scopus_id,
                    "title": title,
                    "authors": authors,
                    "journal": publication,
                    "year": year,
                    "doi": doi,
                    "abstract": abstract,
                    "link": link,
                    "cited_by": cited_by_count,
                    "source": "Scopus"
                })
            except Exception as e:
                print(f"Error parsing Scopus entry: {e}")
                continue
                
        return results

    def search_and_fetch(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Tìm kiếm và lấy chi tiết bài báo
        """
        return self.search(query, max_results, year_start, year_end)

