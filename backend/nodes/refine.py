"""
Node: Refine Query
Cải thiện query dựa trên lý do refinement
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
import json


def refine_query(state: SearchState, gemini: GeminiService) -> SearchState:
    """
    Tự động cải thiện query & strategy:
    - Mở rộng/thu hẹp query
    - Điều chỉnh filters (năm, số lượng)
    - Thay đổi nguồn tìm kiếm
    """
    reason = state['refinement_reason']
    current_strategy = state['search_strategy']
    query_analysis = state['query_analysis']
    user_query = state['user_query']
    
    print(f"\n🔧 Refining query...")
    print(f"   - Reason: {reason}")
    
    prompt = f"""
Kết quả tìm kiếm không đạt yêu cầu. Hãy cải thiện chiến lược:

**Lý do:** {reason}

**Query gốc:** "{user_query}"

**Phân tích:** {json.dumps(query_analysis, indent=2, ensure_ascii=False)}

**Chiến lược hiện tại:**
{json.dumps(current_strategy, indent=2, ensure_ascii=False)}

Đề xuất cải thiện:
1. **new_queries**: Queries mới cho mỗi nguồn (có thể mở rộng keywords, thêm synonyms)
2. **adjust_filters**: Điều chỉnh filters
   - Nếu không có kết quả → mở rộng year_range, tăng max_results
   - Nếu chất lượng kém → thu hẹp query, thêm filters

Trả về JSON (KHÔNG có markdown):
{{
    "new_queries": {{
        "pubmed": "improved PubMed query",
        "scopus": "improved Scopus query",
        "semantic": "improved Semantic query"
    }},
    "adjust_filters": {{
        "year_range": [2015, 2025],
        "max_results_per_source": 20
    }},
    "explanation": "Giải thích ngắn gọn thay đổi"
}}
"""
    
    try:
        response = gemini.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.4
            }
        )
        
        refinement = json.loads(response.text.strip())
        
        # Update strategy
        new_queries = refinement.get('new_queries', {})
        adjust_filters = refinement.get('adjust_filters', {})
        explanation = refinement.get('explanation', 'Query refined')
        
        # Chỉ update queries nếu có trong new_queries
        if 'optimized_queries' not in state['search_strategy']:
            state['search_strategy']['optimized_queries'] = {}
        
        for source_key, new_query in new_queries.items():
            if new_query:
                state['search_strategy']['optimized_queries'][source_key] = new_query
        
        # Update filters
        if adjust_filters:
            state['search_strategy']['filters'].update(adjust_filters)
        
        # Increment refinement count
        state['refinement_count'] = state.get('refinement_count', 0) + 1
        
        print(f"   - Refinement #{state['refinement_count']}")
        print(f"   - Explanation: {explanation}")
        print(f"   - New year range: {state['search_strategy']['filters'].get('year_range')}")
        
        state['messages'].append({
            'role': 'system',
            'content': f"🔧 Refinement #{state['refinement_count']}: {explanation}"
        })
        
    except Exception as e:
        print(f"❌ Refinement Error: {e}")
        
        # Fallback refinement: Mở rộng year range & tăng số lượng
        current_filters = state['search_strategy']['filters']
        year_range = current_filters.get('year_range', [2020, 2025])
        
        # Mở rộng 5 năm về trước
        new_year_start = max(2000, year_range[0] - 5)
        current_filters['year_range'] = [new_year_start, year_range[1]]
        
        # Tăng 50% số lượng
        current_max = current_filters.get('max_results_per_source', 10)
        current_filters['max_results_per_source'] = int(current_max * 1.5)
        
        state['refinement_count'] = state.get('refinement_count', 0) + 1
        
        state['messages'].append({
            'role': 'system',
            'content': f"⚠️  Fallback refinement: expanded year range & increased max results"
        })
    
    return state
