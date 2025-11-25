"""
Backend API cho PubMed Search
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time

class PubMedAPI:
    """Class xử lý tìm kiếm PubMed"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def search(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[str]:
        """
        Tìm kiếm PubMed và trả về danh sách PMIDs
        """
        esearch_url = f"{self.base_url}/esearch.fcgi"
        
        # Build query with date range if provided
        final_query = query
        if year_start and year_end:
            final_query = f"{query} AND {year_start}:{year_end}[pdat]"
        elif year_start:
             final_query = f"{query} AND {year_start}:3000[pdat]"
        
        params = {
            "db": "pubmed",
            "term": final_query,
            "retmax": max_results,
            "retmode": "json"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = requests.get(esearch_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []

    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """
        Lấy chi tiết từ danh sách PMIDs
        """
        if not pmids:
            return []

        ids_str = ",".join(pmids)
        efetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ids_str,
            "retmode": "xml"
        }
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = requests.get(efetch_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            articles = []

            for article in root.findall('.//PubmedArticle'):
                parsed_article = self._parse_article(article)
                if parsed_article:
                    articles.append(parsed_article)

            return articles
        except Exception as e:
            print(f"PubMed fetch error: {e}")
            return []

    def _parse_article(self, article) -> Optional[Dict]:
        """
        Phân tích một bài báo và trích xuất thông tin
        """
        try:
            pmid = article.find('.//PMID').text if article.find('.//PMID') is not None else "N/A"

            # Lấy tiêu đề
            title_elem = article.find('.//ArticleTitle')
            title = ''.join(title_elem.itertext()) if title_elem is not None else "N/A"

            # Lấy tác giả
            authors = []
            author_list = article.findall('.//Author')
            for author in author_list:
                last_name = author.find('LastName')
                fore_name = author.find('ForeName')
                if last_name is not None and fore_name is not None:
                    authors.append(f"{fore_name.text} {last_name.text}")

            # Lấy tóm tắt
            abstract_elem = article.find('.//Abstract/AbstractText')
            abstract = ''.join(abstract_elem.itertext()) if abstract_elem is not None else "N/A"

            # Lấy tên tạp chí
            journal = article.find('.//Journal/Title')
            journal_name = journal.text if journal is not None else "N/A"

            # Lấy năm xuất bản
            year_elem = article.find('.//PubDate/Year')
            if year_elem is not None:
                pub_year = year_elem.text
            else:
                # Try to find MedlineDate if Year is missing
                medline_date = article.find('.//PubDate/MedlineDate')
                pub_year = medline_date.text[:4] if medline_date is not None else "N/A"

            # Lấy DOI
            doi_elem = article.find('.//ArticleId[@IdType="doi"]')
            doi = doi_elem.text if doi_elem is not None else "N/A"
            
            # Lấy PMC ID nếu có
            pmc_elem = article.find('.//ArticleId[@IdType="pmc"]')
            pmc_id = pmc_elem.text if pmc_elem is not None else "N/A"
            
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return {
                "id": pmid,
                "title": title,
                "authors": authors,
                "journal": journal_name,
                "year": pub_year,
                "doi": doi,
                "pmc_id": pmc_id,
                "abstract": abstract,
                "link": link,
                "cited_by": "N/A",  # PubMed API doesn't provide citation count directly
                "source": "PubMed"
            }
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None

    def search_and_fetch(self, query: str, max_results: int = 5, year_start: int = None, year_end: int = None) -> List[Dict]:
        """
        Tìm kiếm và lấy chi tiết bài báo trong một lần gọi
        """
        pmids = self.search(query, max_results, year_start, year_end)
        if pmids:
            return self.fetch_details(pmids)
        return []
