"""
Node: Optimize Queries
Tối ưu query cho từng nguồn riêng biệt
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
import json


def optimize_queries(state: SearchState, gemini: GeminiService) -> SearchState:
    """
    Tạo optimized query cho từng nguồn:
    - PubMed: MeSH terms + Boolean operators
    - Scopus: TITLE-ABS-KEY syntax
    - Semantic Scholar: Natural language (keep Vietnamese if needed)
    """
    user_query = state['user_query']
    analysis = state['query_analysis']
    strategy = state['search_strategy']
    sources = strategy['sources']
    
    optimized_queries = {}
    
    # PubMed optimization
    if 'PubMed' in sources:
        mesh_terms = analysis.get('mesh_terms', [])
        keywords = analysis.get('keywords', [])
        
        prompt_pubmed = f"""
Tạo PubMed query tối ưu từ:
- Original query: "{user_query}"
- Keywords: {', '.join(keywords)}
- MeSH terms: {', '.join(mesh_terms) if mesh_terms else 'N/A'}

Yêu cầu:
- Dùng Boolean operators (AND, OR, NOT)
- Dùng MeSH terms nếu có: [MeSH]
- Format: "term1[MeSH] AND (term2 OR term3)"
- Ngắn gọn, chính xác

Trả về CHỈ query string (KHÔNG giải thích, KHÔNG JSON):
"""
        
        try:
            response = gemini.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt_pubmed,
                config={'temperature': 0.2}
            )
            optimized_queries['pubmed'] = response.text.strip().strip('"\'`')
            print(f"🔍 PubMed query: {optimized_queries['pubmed']}")
        except Exception as e:
            print(f"⚠️  PubMed query optimization failed: {e}")
            optimized_queries['pubmed'] = ' AND '.join(keywords[:3])
    
    # Scopus optimization
    if 'Scopus' in sources:
        keywords = analysis.get('keywords', [])
        
        prompt_scopus = f"""
Tạo Scopus query tối ưu từ:
- Original query: "{user_query}"
- Keywords: {', '.join(keywords)}

Yêu cầu:
- Dùng Scopus syntax: TITLE-ABS-KEY()
- Boolean operators: AND, OR, AND NOT
- Format: TITLE-ABS-KEY("keyword1" AND "keyword2")

Trả về CHỈ query string (KHÔNG giải thích, KHÔNG JSON):
"""
        
        try:
            response = gemini.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt_scopus,
                config={'temperature': 0.2}
            )
            optimized_queries['scopus'] = response.text.strip().strip('"\'`')
            print(f"🔍 Scopus query: {optimized_queries['scopus']}")
        except Exception as e:
            print(f"⚠️  Scopus query optimization failed: {e}")
            keywords_str = '" AND "'.join(keywords[:3])
            optimized_queries['scopus'] = f'TITLE-ABS-KEY("{keywords_str}")'
    
    # Semantic Scholar optimization
    if 'Semantic Scholar' in sources:
        language = analysis.get('language', 'en')
        
        if language == 'vi':
            # Giữ nguyên tiếng Việt hoặc cải thiện nhẹ
            prompt_semantic = f"""
Cải thiện query tiếng Việt cho Semantic Scholar:
"{user_query}"

Yêu cầu:
- Giữ nguyên tiếng Việt
- Ngắn gọn, dễ hiểu
- Ngôn ngữ tự nhiên

Trả về CHỈ query string (KHÔNG giải thích):
"""
        else:
            # Optimize English query
            keywords = analysis.get('keywords', [])
            prompt_semantic = f"""
Tạo Semantic Scholar query từ:
- Original: "{user_query}"
- Keywords: {', '.join(keywords)}

Yêu cầu:
- Ngắn gọn, ngôn ngữ tự nhiên
- Tiếng Anh
- Không cần Boolean operators phức tạp

Trả về CHỈ query string (KHÔNG giải thích):
"""
        
        try:
            response = gemini.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt_semantic,
                config={'temperature': 0.2}
            )
            optimized_queries['semantic'] = response.text.strip().strip('"\'`')
            print(f"🔍 Semantic query: {optimized_queries['semantic']}")
        except Exception as e:
            print(f"⚠️  Semantic query optimization failed: {e}")
            optimized_queries['semantic'] = user_query
    
    # Update strategy với optimized queries
    state['search_strategy']['optimized_queries'] = optimized_queries
    
    # Log
    state['messages'].append({
        'role': 'system',
        'content': f"✅ Optimized {len(optimized_queries)} queries"
    })
    
    return state
