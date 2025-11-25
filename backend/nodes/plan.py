"""
Node: Plan Strategy
Quyết định chiến lược tìm kiếm dựa trên phân tích
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
import json


def plan_strategy(state: SearchState, gemini: GeminiService) -> SearchState:
    """
    Quyết định:
    - Nguồn nào? (PubMed/Scopus/Semantic Scholar)
    - Filters (năm, số lượng)
    - Priority
    
    Rules:
    - Medical → PubMed priority
    - Engineering/CS → Scopus priority
    - Vietnamese → Must include Semantic Scholar
    - Review/Meta-analysis → Recent years, nhiều nguồn
    """
    analysis = state['query_analysis']
    preferences = state['user_preferences']
    
    # Get user-selected sources (nếu có)
    user_sources = preferences.get('sources', [])
    
    prompt = f"""
Dựa trên phân tích query và preferences, đề xuất chiến lược tìm kiếm tối ưu:

**Phân tích Query:**
{json.dumps(analysis, indent=2, ensure_ascii=False)}

**User Preferences:**
- Max results: {preferences.get('max_results', 10)}
- Year range: {preferences.get('year_range', [2020, 2025])}
- Preferred sources: {', '.join(user_sources) if user_sources else 'Auto-select'}

**Quy tắc:**
1. Nếu topic="medical" → Ưu tiên PubMed
2. Nếu topic="engineering"/"computer_science" → Ưu tiên Scopus
3. Nếu language="vi" → BẮT BUỘC có Semantic Scholar
4. Nếu intent="review"/"meta_analysis" → Tìm nhiều nguồn, năm gần đây
5. Nếu user đã chọn sources → Tôn trọng lựa chọn của user

Trả về JSON (KHÔNG có markdown):
{{
    "sources": ["PubMed", "Scopus", "Semantic Scholar"],
    "source_priority": "PubMed > Scopus > Semantic Scholar",
    "parallel_search": true,
    "filters": {{
        "year_range": [2020, 2025],
        "max_results_per_source": 15
    }},
    "reason": "Giải thích ngắn gọn tại sao chọn chiến lược này"
}}
"""
    
    try:
        response = gemini.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.3
            }
        )
        
        strategy_text = response.text.strip()
        strategy = json.loads(strategy_text)
        
        # Override with user preferences if specified
        if user_sources:
            strategy['sources'] = user_sources
        
        if 'year_range' in preferences:
            strategy['filters']['year_range'] = preferences['year_range']
        
        if 'max_results' in preferences:
            # Chia đều cho các sources
            num_sources = len(strategy['sources'])
            per_source = max(5, preferences['max_results'] // num_sources)
            strategy['filters']['max_results_per_source'] = per_source
        
        state['search_strategy'] = strategy
        
        # Log
        state['messages'].append({
            'role': 'system',
            'content': f"✅ Strategy: {', '.join(strategy['sources'])}"
        })
        
        print(f"📋 Search Strategy:")
        print(f"   - Sources: {', '.join(strategy['sources'])}")
        print(f"   - Priority: {strategy.get('source_priority')}")
        print(f"   - Reason: {strategy.get('reason')}")
        
    except Exception as e:
        print(f"❌ Strategy Planning Error: {e}")
        
        # Fallback strategy
        sources = user_sources if user_sources else ['PubMed', 'Semantic Scholar']
        year_range = preferences.get('year_range', [2020, 2025])
        max_per_source = max(5, preferences.get('max_results', 10) // len(sources))
        
        state['search_strategy'] = {
            "sources": sources,
            "source_priority": " > ".join(sources),
            "parallel_search": True,
            "filters": {
                "year_range": year_range,
                "max_results_per_source": max_per_source
            },
            "reason": "Fallback strategy due to planning error"
        }
        
        state['messages'].append({
            'role': 'system',
            'content': "⚠️  Using fallback strategy"
        })
    
    return state
