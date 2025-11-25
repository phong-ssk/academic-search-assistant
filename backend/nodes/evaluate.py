"""
Node: Evaluate Results
Đánh giá chất lượng kết quả & quyết định refine
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
from ..async_apis import AsyncSearchAPIs
import json


def evaluate_results(state: SearchState, gemini: GeminiService, async_apis: AsyncSearchAPIs) -> SearchState:
    """
    Đánh giá:
    - Quality score (0.0-1.0)
    - Needs refinement?
    - Deduplicate & merge results
    
    Tiêu chí dừng tìm kiếm:
    1. Quality score >= 0.7 (good)
    2. Tìm được >= 80% số lượng mong muốn
    3. Đã refine 2 lần
    """
    results_dict = state['search_results']
    user_query = state['user_query']
    query_analysis = state['query_analysis']
    preferences = state['user_preferences']
    refinement_count = state.get('refinement_count', 0)
    
    # Count total results
    total_count = sum(len(articles) for articles in results_dict.values())
    
    # Basic check: No results
    if total_count == 0:
        state['needs_refinement'] = True
        state['refinement_reason'] = "No results found"
        state['quality_score'] = 0.0
        state['final_results'] = []
        state['messages'].append({
            'role': 'system',
            'content': "⚠️  No results found, needs refinement"
        })
        return state
    
    # Deduplicate & merge
    print(f"\n🔍 Deduplicating {total_count} articles...")
    unique_articles = async_apis.deduplicate_results(results_dict)
    
    state['final_results'] = unique_articles
    
    # Check if we have enough results (80% of requested)
    requested = preferences.get('max_results', 10)
    has_enough = len(unique_articles) >= requested * 0.8
    
    # Collect sample titles for AI evaluation
    sample_titles = {}
    for source, articles in results_dict.items():
        sample_titles[source] = [a.get('title', 'N/A') for a in articles[:3]]
    
    # AI-based evaluation
    prompt = f"""
Đánh giá chất lượng kết quả tìm kiếm học thuật:

**Query gốc:** "{user_query}"

**Phân tích query:**
{json.dumps(query_analysis, indent=2, ensure_ascii=False)}

**Kết quả:**
- Tổng số: {total_count} articles (sau loại trùng: {len(unique_articles)})
- Số lượng mong muốn: {requested}
- Đã refine: {refinement_count} lần

**Sample titles từ mỗi nguồn:**
{json.dumps(sample_titles, indent=2, ensure_ascii=False)}

Đánh giá:
1. Các titles có LIÊN QUAN đến query không?
2. Chất lượng overall: excellent/good/fair/poor
3. Có cần refine query không?

Trả về JSON (KHÔNG có markdown):
{{
    "quality_score": 0.85,
    "needs_refinement": false,
    "reason": "Kết quả liên quan tốt, đủ số lượng",
    "suggestions": ""
}}

Lưu ý:
- quality_score >= 0.7 → good (không cần refine)
- quality_score < 0.5 → poor (cần refine)
- Nếu đã refine 2 lần → KHÔNG refine nữa
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
        
        evaluation = json.loads(response.text.strip())
        
        quality_score = float(evaluation.get('quality_score', 0.5))
        needs_refinement = evaluation.get('needs_refinement', False)
        reason = evaluation.get('reason', '')
        
        # Override: Không refine nếu đã refine 2 lần
        if refinement_count >= 2:
            needs_refinement = False
            reason = "Max refinement attempts reached (2)"
        
        # Override: Không refine nếu đủ kết quả và quality OK
        if has_enough and quality_score >= 0.6:
            needs_refinement = False
            reason = "Sufficient results with acceptable quality"
        
        state['quality_score'] = quality_score
        state['needs_refinement'] = needs_refinement
        state['refinement_reason'] = reason
        
        print(f"\n📊 Evaluation:")
        print(f"   - Quality Score: {quality_score:.2f}")
        print(f"   - Unique Articles: {len(unique_articles)}/{total_count}")
        print(f"   - Needs Refinement: {needs_refinement}")
        print(f"   - Reason: {reason}")
        
        state['messages'].append({
            'role': 'system',
            'content': f"✅ Quality: {quality_score:.2f}, Articles: {len(unique_articles)}"
        })
        
    except Exception as e:
        print(f"❌ Evaluation Error: {e}")
        
        # Fallback evaluation
        quality_score = 0.7 if has_enough else 0.4
        needs_refinement = not has_enough and refinement_count < 2
        
        state['quality_score'] = quality_score
        state['needs_refinement'] = needs_refinement
        state['refinement_reason'] = "Fallback evaluation"
        
        state['messages'].append({
            'role': 'system',
            'content': "⚠️  Using fallback evaluation"
        })
    
    # Add metadata
    state['metadata'] = {
        'total_found': total_count,
        'unique_count': len(unique_articles),
        'quality_score': state['quality_score'],
        'refinement_count': refinement_count,
        'sources_used': list(results_dict.keys())
    }
    
    return state
