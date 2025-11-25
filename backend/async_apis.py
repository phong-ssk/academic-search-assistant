"""
Async API Wrappers with Caching & Deduplication
Tối ưu hóa: Cache, Early stopping, Rate limiting
"""
import asyncio
import aiohttp
import hashlib
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .pubmed_api import PubMedAPI
from .scopus_api import ScopusAPI
from .semantic_scholar_api import SemanticScholarAPI


class SearchCache:
    """Simple in-memory cache với TTL"""
    def __init__(self, ttl_minutes: int = 30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _make_key(self, source: str, query: str, params: Dict) -> str:
        """Tạo unique key cho cache"""
        params_str = json.dumps(params, sort_keys=True)
        key_str = f"{source}:{query}:{params_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, source: str, query: str, params: Dict) -> Optional[List[Dict]]:
        """Lấy từ cache nếu còn hạn"""
        key = self._make_key(source, query, params)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                print(f"✅ Cache HIT for {source}: {query[:50]}...")
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, source: str, query: str, params: Dict, data: List[Dict]):
        """Lưu vào cache"""
        key = self._make_key(source, query, params)
        self.cache[key] = (data, datetime.now())
        print(f"💾 Cached {len(data)} results for {source}")


class ArticleDeduplicator:
    """Loại bỏ trùng lặp dựa trên DOI, PMID, Title similarity"""
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """Chuẩn hóa title để so sánh"""
        import re
        title = title.lower().strip()
        title = re.sub(r'[^\w\s]', '', title)  # Loại bỏ ký tự đặc biệt
        title = re.sub(r'\s+', ' ', title)  # Loại bỏ khoảng trắng thừa
        return title
    
    @staticmethod
    def are_titles_similar(title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Kiểm tra 2 title có giống nhau không (Jaccard similarity)"""
        from difflib import SequenceMatcher
        
        t1 = ArticleDeduplicator.normalize_title(title1)
        t2 = ArticleDeduplicator.normalize_title(title2)
        
        # Sử dụng SequenceMatcher cho tốc độ
        ratio = SequenceMatcher(None, t1, t2).ratio()
        return ratio >= threshold
    
    @staticmethod
    def deduplicate(articles: List[Dict]) -> List[Dict]:
        """
        Loại bỏ trùng lặp với priority:
        1. DOI (highest priority)
        2. PMID (PubMed ID)
        3. Title similarity (fallback)
        """
        seen_dois = set()
        seen_pmids = set()
        seen_titles = []
        unique_articles = []
        
        for article in articles:
            # Check DOI
            doi = article.get('doi', '').strip()
            if doi and doi != 'N/A':
                if doi in seen_dois:
                    print(f"⚠️  Duplicate DOI: {doi}")
                    continue
                seen_dois.add(doi)
                unique_articles.append(article)
                continue
            
            # Check PMID
            pmid = article.get('pmid', '').strip()
            if pmid and pmid != 'N/A':
                if pmid in seen_pmids:
                    print(f"⚠️  Duplicate PMID: {pmid}")
                    continue
                seen_pmids.add(pmid)
                unique_articles.append(article)
                continue
            
            # Check Title similarity
            title = article.get('title', '').strip()
            if not title:
                unique_articles.append(article)
                continue
            
            is_duplicate = False
            for seen_title in seen_titles:
                if ArticleDeduplicator.are_titles_similar(title, seen_title):
                    print(f"⚠️  Duplicate Title: {title[:60]}...")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_titles.append(title)
                unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            print(f"🗑️  Removed {removed} duplicates from {len(articles)} articles")
        
        return unique_articles


class AsyncSearchAPIs:
    """Async wrappers cho PubMed, Scopus, Semantic Scholar với tối ưu hóa"""
    
    def __init__(self, pubmed_key: str = None, scopus_key: str = None, semantic_key: str = None):
        self.pubmed = PubMedAPI(pubmed_key)
        self.scopus = ScopusAPI(scopus_key)
        self.semantic = SemanticScholarAPI(semantic_key)
        self.cache = SearchCache(ttl_minutes=30)
        self.deduplicator = ArticleDeduplicator()
    
    async def search_pubmed_async(self, query: str, max_results: int = 10, 
                                  year_start: int = None, year_end: int = None) -> List[Dict]:
        """Async PubMed search với cache"""
        params = {'max_results': max_results, 'year_start': year_start, 'year_end': year_end}
        
        # Check cache
        cached = self.cache.get('PubMed', query, params)
        if cached is not None:
            return cached
        
        # Execute search in thread pool (vì API sync)
        loop = asyncio.get_event_loop()
        try:
            results = await loop.run_in_executor(
                None, 
                self.pubmed.search_and_fetch, 
                query, max_results, year_start, year_end
            )
            
            # Cache results
            self.cache.set('PubMed', query, params, results)
            return results
        except Exception as e:
            print(f"❌ PubMed Error: {e}")
            return []
    
    async def search_scopus_async(self, query: str, max_results: int = 10, 
                                  year_start: int = None, year_end: int = None) -> List[Dict]:
        """Async Scopus search với cache"""
        params = {'max_results': max_results, 'year_start': year_start, 'year_end': year_end}
        
        # Check cache
        cached = self.cache.get('Scopus', query, params)
        if cached is not None:
            return cached
        
        # Execute search
        loop = asyncio.get_event_loop()
        try:
            results = await loop.run_in_executor(
                None, 
                self.scopus.search_and_fetch, 
                query, max_results, year_start, year_end
            )
            
            # Cache results
            self.cache.set('Scopus', query, params, results)
            return results
        except Exception as e:
            print(f"❌ Scopus Error: {e}")
            return []
    
    async def search_semantic_async(self, query: str, max_results: int = 10, 
                                    year_start: int = None, year_end: int = None) -> List[Dict]:
        """Async Semantic Scholar search với cache"""
        params = {'max_results': max_results, 'year_start': year_start, 'year_end': year_end}
        
        # Check cache
        cached = self.cache.get('Semantic', query, params)
        if cached is not None:
            return cached
        
        # Execute search
        loop = asyncio.get_event_loop()
        try:
            results = await loop.run_in_executor(
                None, 
                self.semantic.search_and_fetch, 
                query, max_results, year_start, year_end
            )
            
            # Cache results
            self.cache.set('Semantic', query, params, results)
            return results
        except Exception as e:
            print(f"❌ Semantic Scholar Error: {e}")
            return []
    
    async def search_all_parallel(self, queries: Dict[str, str], 
                                  max_results_per_source: int = 10,
                                  year_start: int = None, 
                                  year_end: int = None) -> Dict[str, List[Dict]]:
        """
        Tìm kiếm song song trên tất cả nguồn với Early Stopping
        
        queries = {
            'pubmed': 'query string',
            'scopus': 'query string',
            'semantic': 'query string'
        }
        """
        tasks = []
        sources = []
        
        # PubMed
        if 'pubmed' in queries and queries['pubmed']:
            tasks.append(self.search_pubmed_async(
                queries['pubmed'], max_results_per_source, year_start, year_end
            ))
            sources.append('PubMed')
        
        # Scopus
        if 'scopus' in queries and queries['scopus']:
            tasks.append(self.search_scopus_async(
                queries['scopus'], max_results_per_source, year_start, year_end
            ))
            sources.append('Scopus')
        
        # Semantic Scholar
        if 'semantic' in queries and queries['semantic']:
            tasks.append(self.search_semantic_async(
                queries['semantic'], max_results_per_source, year_start, year_end
            ))
            sources.append('Semantic Scholar')
        
        # Execute parallel với timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=60.0  # 60s timeout
            )
        except asyncio.TimeoutError:
            print("⚠️  Search timeout after 60s")
            results = [[] for _ in tasks]
        
        # Map results to sources
        result_dict = {}
        for i, source in enumerate(sources):
            if isinstance(results[i], Exception):
                print(f"❌ {source} failed: {results[i]}")
                result_dict[source] = []
            else:
                result_dict[source] = results[i]
        
        return result_dict
    
    def deduplicate_results(self, results_dict: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Merge & deduplicate kết quả từ nhiều nguồn
        Priority: PubMed > Scopus > Semantic Scholar
        """
        all_articles = []
        
        # Thêm theo thứ tự priority
        for source in ['PubMed', 'Scopus', 'Semantic Scholar']:
            if source in results_dict:
                all_articles.extend(results_dict[source])
        
        # Deduplicate
        unique_articles = self.deduplicator.deduplicate(all_articles)
        
        return unique_articles
