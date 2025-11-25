"""
Search Manager - Orchestrates the search process
"""
from typing import List, Dict, Any
from .pubmed_api import PubMedAPI
from .scopus_api import ScopusAPI
from .semantic_scholar_api import SemanticScholarAPI
from .gemini_service import GeminiService

class SearchManager:
    def __init__(self, pubmed_key: str = None, scopus_key: str = None, gemini_key: str = None, semantic_key: str = None):
        self.pubmed = PubMedAPI(pubmed_key)
        self.scopus = ScopusAPI(scopus_key)
        self.semantic = SemanticScholarAPI(semantic_key)
        self.gemini = GeminiService(gemini_key)

    def process_search_with_custom_queries(self,
                                           english_query: str,
                                           vietnamese_query: str,
                                           sources: List[str],
                                           max_results: int = 5,
                                           year_start: int = None,
                                           year_end: int = None,
                                           search_mode: str = "Original") -> Dict[str, Any]:
        """
        Thực hiện tìm kiếm với query tùy chỉnh cho từng nguồn
        """
        results = {
            "search_mode": search_mode,
            "queries_used": {
                "english": english_query,
                "vietnamese": vietnamese_query
            },
            "articles": [],
            "errors": []
        }

        all_articles = []

        # PubMed (English only)
        if "PubMed" in sources:
            try:
                pubmed_results = self.pubmed.search_and_fetch(english_query, max_results, year_start, year_end)
                all_articles.extend(pubmed_results)
            except Exception as e:
                results["errors"].append(f"PubMed Error: {e}")

        # Scopus (English only)
        if "Scopus" in sources:
            try:
                scopus_results = self.scopus.search_and_fetch(english_query, max_results, year_start, year_end)
                all_articles.extend(scopus_results)
            except Exception as e:
                results["errors"].append(f"Scopus Error: {e}")

        # Semantic Scholar (Vietnamese/English)
        if "Semantic Scholar" in sources:
            try:
                semantic_results = self.semantic.search_and_fetch(vietnamese_query, max_results, year_start, year_end)
                all_articles.extend(semantic_results)
            except Exception as e:
                results["errors"].append(f"Semantic Scholar Error: {e}")

        results["articles"] = all_articles
        return results

    def process_search(self, 
                      user_query: str, 
                      sources: List[str], 
                      max_results: int = 5,
                      year_start: int = None,
                      year_end: int = None,
                      use_ai_optimization: bool = True) -> Dict[str, Any]:
        """
        Thực hiện quy trình tìm kiếm đầy đủ (legacy method - kept for backward compatibility)
        """
        results = {
            "optimization": None,
            "articles": [],
            "errors": []
        }

        # 1. AI Optimization
        english_query = user_query
        vietnamese_query = user_query
        
        if use_ai_optimization and self.gemini.api_key:
            try:
                opt_result = self.gemini.optimize_query(user_query)
                results["optimization"] = opt_result
                english_query = opt_result.get("english_query", user_query)
                vietnamese_query = opt_result.get("vietnamese_query", user_query)
            except Exception as e:
                results["errors"].append(f"AI Optimization failed: {e}")

        # 2. Execute Searches
        all_articles = []

        # PubMed (English)
        if "PubMed" in sources:
            try:
                pubmed_results = self.pubmed.search_and_fetch(english_query, max_results, year_start, year_end)
                all_articles.extend(pubmed_results)
            except Exception as e:
                results["errors"].append(f"PubMed Error: {e}")

        # Scopus (English)
        if "Scopus" in sources:
            try:
                scopus_results = self.scopus.search_and_fetch(english_query, max_results, year_start, year_end)
                all_articles.extend(scopus_results)
            except Exception as e:
                results["errors"].append(f"Scopus Error: {e}")

        # Semantic Scholar (Vietnamese/English - Context dependent, but user asked for VN support here)
        # If query looks Vietnamese or user asked for VN search, Semantic Scholar is good.
        # We will search Semantic Scholar with the Vietnamese query if available, or original.
        if "Semantic Scholar" in sources:
            try:
                # Prefer Vietnamese query for Semantic Scholar if it differs from English and original was likely VN
                # Or just search both? For now, let's use the optimized Vietnamese query if we have it.
                search_query = vietnamese_query if vietnamese_query != english_query else user_query
                semantic_results = self.semantic.search_and_fetch(search_query, max_results, year_start, year_end)
                all_articles.extend(semantic_results)
            except Exception as e:
                results["errors"].append(f"Semantic Scholar Error: {e}")

        results["articles"] = all_articles
        return results

    def consult(self, query: str) -> str:
        return self.gemini.consult_search(query)
