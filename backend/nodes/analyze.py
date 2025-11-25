"""
Node: Analyze Query
Phân tích yêu cầu người dùng bằng Gemini AI
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
import json


def analyze_query(state: SearchState, gemini: GeminiService) -> SearchState:
    """
    Phân tích query của user:
    - Topic: medical/engineering/social/other
    - Intent: review/rct/case_study/general
    - Language: vi/en/mixed
    - Complexity: simple/medium/complex
    - Keywords & MeSH terms
    """
    user_query = state['user_query']
    
    prompt = f"""
Phân tích yêu cầu tìm kiếm học thuật sau và trả về JSON:

Query: "{user_query}"

Hãy xác định:
1. **topic**: Chủ đề chính (medical, engineering, computer_science, social_science, biology, physics, other)
2. **intent**: Mục đích tìm kiếm (review, clinical_trial, case_study, meta_analysis, general_research)
3. **language**: Ngôn ngữ (vi, en, mixed)
4. **complexity**: Độ phức tạp (simple, medium, complex)
5. **keywords**: Danh sách từ khóa quan trọng (3-7 từ)
6. **mesh_terms**: MeSH terms (nếu là y học, nếu không thì để [])

Trả về CHÍNH XÁC JSON format (KHÔNG có markdown):
{{
    "topic": "medical",
    "intent": "review",
    "language": "vi",
    "complexity": "medium",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "mesh_terms": ["MeSH term1", "MeSH term2"]
}}
"""
    
    try:
        # Call Gemini
        response = gemini.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.3
            }
        )
        
        analysis_text = response.text.strip()
        
        # Parse JSON
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback nếu không parse được
            print(f"⚠️  Cannot parse JSON, using defaults")
            analysis = {
                "topic": "general",
                "intent": "general_research",
                "language": "en",
                "complexity": "medium",
                "keywords": user_query.split()[:5],
                "mesh_terms": []
            }
        
        state['query_analysis'] = analysis
        
        # Log message
        state['messages'].append({
            'role': 'system',
            'content': f"✅ Analyzed query: topic={analysis.get('topic')}, language={analysis.get('language')}"
        })
        
        print(f"📊 Query Analysis:")
        print(f"   - Topic: {analysis.get('topic')}")
        print(f"   - Intent: {analysis.get('intent')}")
        print(f"   - Language: {analysis.get('language')}")
        print(f"   - Keywords: {', '.join(analysis.get('keywords', [])[:3])}")
        
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        # Fallback analysis
        state['query_analysis'] = {
            "topic": "general",
            "intent": "general_research",
            "language": "en",
            "complexity": "medium",
            "keywords": user_query.split()[:5],
            "mesh_terms": []
        }
        state['messages'].append({
            'role': 'system',
            'content': f"⚠️  Analysis failed, using defaults"
        })
    
    return state
