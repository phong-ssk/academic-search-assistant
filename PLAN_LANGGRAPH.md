# 🧠 Plan: LangGraph Orchestration cho Academic Search

## 🎯 Mục Tiêu

Xây dựng `app_langgraph.py` sử dụng LangGraph để tự động điều phối quy trình tìm kiếm thông minh, thay thế logic đơn giản hiện tại bằng AI agent có khả năng:

1. **Phân tích yêu cầu** của người dùng
2. **Quyết định chiến lược** tìm kiếm (nguồn nào, query nào)
3. **Điều phối song song** các API
4. **Tổng hợp & đánh giá** kết quả
5. **Tự động tối ưu** nếu kết quả không đủ

---

## 🏗️ Kiến Trúc LangGraph

### Graph Structure

```
                    START
                      ↓
            ┌─────────────────┐
            │  ANALYZE_QUERY  │ ← Phân tích yêu cầu người dùng
            └─────────────────┘
                      ↓
            ┌─────────────────┐
            │  PLAN_STRATEGY  │ ← AI quyết định:
            └─────────────────┘   - Nguồn nào? (PubMed/Scopus/Semantic)
                      ↓           - Query EN/VN như thế nào?
            ┌─────────────────┐   - Bộ lọc gì? (năm, số lượng)
            │ OPTIMIZE_QUERIES│ ← Tối ưu query cho từng nguồn
            └─────────────────┘
                      ↓
            ┌─────────────────┐
            │  EXECUTE_SEARCH │ ← Gọi API song song
            └─────────────────┘   (PubMed + Scopus + Semantic)
                      ↓
            ┌─────────────────┐
            │ EVALUATE_RESULTS│ ← Đánh giá chất lượng kết quả
            └─────────────────┘
                      ↓
                 ┌─────┐
                 │ OK? │
                 └─────┘
                 ↙     ↘
              YES       NO
               ↓         ↓
            ┌────┐  ┌─────────────┐
            │END │  │REFINE_QUERY │ → quay lại OPTIMIZE_QUERIES
            └────┘  └─────────────┘
```

---

## 📦 State Schema

```python
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph

class SearchState(TypedDict):
    # Input
    user_query: str
    user_preferences: Dict  # {max_results, year_range, sources}
    
    # Analysis
    query_analysis: Dict  # {intent, topic, language, complexity}
    
    # Planning
    search_strategy: Dict  # {
    #   sources: List[str],
    #   queries: {en: str, vn: str},
    #   filters: {...},
    #   priority: str
    # }
    
    # Execution
    search_results: Dict  # {source: [articles]}
    
    # Evaluation
    quality_score: float
    needs_refinement: bool
    refinement_reason: str
    
    # Output
    final_results: List[Dict]
    metadata: Dict
```

---

## 🔧 Nodes (Chức Năng Từng Bước)

### 1. ANALYZE_QUERY
**Input:** `user_query`, `user_preferences`  
**Output:** `query_analysis`

**Logic:**
```python
def analyze_query(state: SearchState) -> SearchState:
    """
    Dùng Gemini phân tích:
    - Chủ đề: Y học, Kỹ thuật, Khoa học xã hội?
    - Ý định: Tìm review? RCT? Case study?
    - Ngôn ngữ: Tiếng Việt hay Anh?
    - Độ phức tạp: Đơn giản/Phức tạp/Chuyên sâu
    """
    prompt = f"""
    Phân tích yêu cầu tìm kiếm sau:
    "{state['user_query']}"
    
    Trả về JSON:
    {{
        "topic": "medical/engineering/social/...",
        "intent": "review/rct/case_study/general",
        "language": "vi/en/mixed",
        "complexity": "simple/medium/complex",
        "keywords": ["key1", "key2", ...],
        "mesh_terms": ["term1", "term2", ...] # nếu là y học
    }}
    """
    analysis = gemini.generate(prompt, json_mode=True)
    state["query_analysis"] = analysis
    return state
```

---

### 2. PLAN_STRATEGY
**Input:** `query_analysis`, `user_preferences`  
**Output:** `search_strategy`

**Logic:**
```python
def plan_strategy(state: SearchState) -> SearchState:
    """
    Quyết định chiến lược dựa trên phân tích:
    
    Rules:
    - Nếu topic="medical" → Ưu tiên PubMed
    - Nếu topic="engineering" → Ưu tiên Scopus
    - Nếu language="vi" → Bắt buộc có Semantic Scholar
    - Nếu intent="review" → Tìm nhiều nguồn, filter năm gần
    - Nếu complexity="complex" → Dùng advanced query với Boolean
    """
    
    analysis = state["query_analysis"]
    
    # AI-based decision
    prompt = f"""
    Dựa trên phân tích:
    {json.dumps(analysis, indent=2)}
    
    Người dùng muốn tìm: {state['user_preferences']}
    
    Hãy đề xuất chiến lược tìm kiếm tối ưu:
    {{
        "sources": ["PubMed", "Scopus", "Semantic Scholar"],
        "source_priority": "PubMed > Scopus > Semantic",
        "parallel_search": true,
        "filters": {{
            "year_range": [2020, 2025],
            "max_results_per_source": 30
        }},
        "reason": "Giải thích tại sao chọn chiến lược này"
    }}
    """
    
    strategy = gemini.generate(prompt, json_mode=True)
    state["search_strategy"] = strategy
    return state
```

---

### 3. OPTIMIZE_QUERIES
**Input:** `user_query`, `query_analysis`, `search_strategy`  
**Output:** `search_strategy` (updated with optimized queries)

**Logic:**
```python
def optimize_queries(state: SearchState) -> SearchState:
    """
    Tối ưu query cho TỪNG nguồn riêng biệt
    """
    analysis = state["query_analysis"]
    strategy = state["search_strategy"]
    
    optimized = {}
    
    # PubMed: MeSH terms + Boolean
    if "PubMed" in strategy["sources"]:
        prompt_pubmed = f"""
        Tạo PubMed query từ: "{state['user_query']}"
        
        Yêu cầu:
        - Dùng MeSH terms: {analysis.get('mesh_terms', [])}
        - Dùng Boolean operators (AND, OR, NOT)
        - Format: "term1[MeSH] AND (term2 OR term3)"
        
        Trả về query duy nhất (không giải thích):
        """
        optimized["pubmed"] = gemini.generate(prompt_pubmed).strip()
    
    # Scopus: Scopus syntax
    if "Scopus" in strategy["sources"]:
        prompt_scopus = f"""
        Tạo Scopus query từ: "{state['user_query']}"
        
        Dùng Scopus syntax:
        - TITLE-ABS-KEY()
        - AND, OR, AND NOT
        
        Ví dụ: TITLE-ABS-KEY("machine learning" AND "healthcare")
        
        Trả về query:
        """
        optimized["scopus"] = gemini.generate(prompt_scopus).strip()
    
    # Semantic Scholar: Tiếng Việt hoặc Anh tự nhiên
    if "Semantic Scholar" in strategy["sources"]:
        if analysis["language"] == "vi":
            # Giữ nguyên tiếng Việt hoặc cải thiện
            optimized["semantic"] = state["user_query"]
        else:
            # Tối ưu tiếng Anh
            prompt_semantic = f"""
            Cải thiện query cho Semantic Scholar: "{state['user_query']}"
            
            Yêu cầu: Ngắn gọn, dễ hiểu, ngôn ngữ tự nhiên
            
            Trả về query:
            """
            optimized["semantic"] = gemini.generate(prompt_semantic).strip()
    
    state["search_strategy"]["optimized_queries"] = optimized
    return state
```

---

### 4. EXECUTE_SEARCH
**Input:** `search_strategy`  
**Output:** `search_results`

**Logic:**
```python
import asyncio

async def execute_search(state: SearchState) -> SearchState:
    """
    Thực thi tìm kiếm SONG SONG trên các nguồn
    """
    strategy = state["search_strategy"]
    queries = strategy["optimized_queries"]
    filters = strategy["filters"]
    
    async def search_pubmed():
        if "pubmed" in queries:
            return await pubmed_api.search_async(
                query=queries["pubmed"],
                max_results=filters["max_results_per_source"],
                year_start=filters["year_range"][0],
                year_end=filters["year_range"][1]
            )
        return []
    
    async def search_scopus():
        if "scopus" in queries:
            return await scopus_api.search_async(
                query=queries["scopus"],
                max_results=filters["max_results_per_source"],
                year_start=filters["year_range"][0],
                year_end=filters["year_range"][1]
            )
        return []
    
    async def search_semantic():
        if "semantic" in queries:
            return await semantic_api.search_async(
                query=queries["semantic"],
                max_results=filters["max_results_per_source"],
                year_start=filters["year_range"][0],
                year_end=filters["year_range"][1]
            )
        return []
    
    # Parallel execution
    results = await asyncio.gather(
        search_pubmed(),
        search_scopus(),
        search_semantic()
    )
    
    state["search_results"] = {
        "PubMed": results[0],
        "Scopus": results[1],
        "Semantic Scholar": results[2]
    }
    
    return state
```

---

### 5. EVALUATE_RESULTS
**Input:** `search_results`, `query_analysis`  
**Output:** `quality_score`, `needs_refinement`, `final_results`

**Logic:**
```python
def evaluate_results(state: SearchState) -> SearchState:
    """
    Đánh giá chất lượng kết quả & quyết định có cần refine không
    """
    results = state["search_results"]
    total_count = sum(len(articles) for articles in results.values())
    
    # Basic checks
    if total_count == 0:
        state["needs_refinement"] = True
        state["refinement_reason"] = "No results found"
        state["quality_score"] = 0.0
        return state
    
    # AI-based evaluation
    prompt = f"""
    Đánh giá chất lượng kết quả tìm kiếm:
    
    Query gốc: "{state['user_query']}"
    Phân tích: {state['query_analysis']}
    
    Kết quả:
    - PubMed: {len(results.get('PubMed', []))} bài
    - Scopus: {len(results.get('Scopus', []))} bài
    - Semantic Scholar: {len(results.get('Semantic Scholar', []))} bài
    
    Top 3 titles từ mỗi nguồn:
    {json.dumps([r['title'] for r in results.get('PubMed', [])[:3]])}
    {json.dumps([r['title'] for r in results.get('Scopus', [])[:3]])}
    {json.dumps([r['title'] for r in results.get('Semantic Scholar', [])[:3]])}
    
    Đánh giá:
    {{
        "quality_score": 0.0-1.0,  # 0=không liên quan, 1=rất liên quan
        "needs_refinement": true/false,
        "reason": "Giải thích",
        "suggestions": "Gợi ý cải thiện (nếu cần)"
    }}
    """
    
    evaluation = gemini.generate(prompt, json_mode=True)
    
    state["quality_score"] = evaluation["quality_score"]
    state["needs_refinement"] = evaluation["needs_refinement"]
    state["refinement_reason"] = evaluation.get("reason", "")
    
    # Merge and deduplicate results
    all_articles = []
    seen_dois = set()
    
    for source, articles in results.items():
        for article in articles:
            doi = article.get("doi", "")
            if doi and doi != "N/A":
                if doi not in seen_dois:
                    seen_dois.add(doi)
                    all_articles.append(article)
            else:
                # No DOI, add anyway but may have duplicates
                all_articles.append(article)
    
    state["final_results"] = all_articles
    
    return state
```

---

### 6. REFINE_QUERY
**Input:** `refinement_reason`, `search_strategy`  
**Output:** `search_strategy` (updated)

**Logic:**
```python
def refine_query(state: SearchState) -> SearchState:
    """
    Tự động cải thiện query dựa trên lý do refinement
    """
    reason = state["refinement_reason"]
    current_strategy = state["search_strategy"]
    
    prompt = f"""
    Kết quả tìm kiếm không đạt yêu cầu.
    
    Lý do: {reason}
    Chiến lược hiện tại: {json.dumps(current_strategy, indent=2)}
    
    Hãy đề xuất cải thiện:
    {{
        "new_queries": {{
            "pubmed": "...",
            "scopus": "...",
            "semantic": "..."
        }},
        "adjust_filters": {{
            "year_range": [2015, 2025],  # Mở rộng phạm vi
            "max_results_per_source": 50  # Tăng số lượng
        }},
        "explanation": "Giải thích thay đổi"
    }}
    """
    
    refinement = gemini.generate(prompt, json_mode=True)
    
    # Update strategy
    state["search_strategy"]["optimized_queries"] = refinement["new_queries"]
    state["search_strategy"]["filters"] = refinement["adjust_filters"]
    
    return state
```

---

## 🔄 Conditional Edges

```python
def should_refine(state: SearchState) -> str:
    """
    Quyết định có nên refine query không
    
    Max 2 lần refinement để tránh vòng lặp vô hạn
    """
    if not state["needs_refinement"]:
        return "END"
    
    # Check refinement count
    refinement_count = state.get("refinement_count", 0)
    if refinement_count >= 2:
        # Đã refine 2 lần, dừng lại
        return "END"
    
    state["refinement_count"] = refinement_count + 1
    return "REFINE"
```

---

## 🛠️ Implementation Plan

### Phase 1: Setup
```bash
pip install langgraph langchain-google-genai langchain-core
```

### Phase 2: File Structure
```
backend/
├── langgraph_orchestrator.py  # LangGraph logic
├── nodes/
│   ├── analyze.py
│   ├── plan.py
│   ├── optimize.py
│   ├── execute.py
│   ├── evaluate.py
│   └── refine.py
└── async_apis.py  # Async wrappers for PubMed/Scopus/Semantic
```

### Phase 3: Build Graph
```python
from langgraph.graph import StateGraph, END

def build_search_graph():
    workflow = StateGraph(SearchState)
    
    # Add nodes
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("plan_strategy", plan_strategy)
    workflow.add_node("optimize_queries", optimize_queries)
    workflow.add_node("execute_search", execute_search)
    workflow.add_node("evaluate_results", evaluate_results)
    workflow.add_node("refine_query", refine_query)
    
    # Add edges
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "plan_strategy")
    workflow.add_edge("plan_strategy", "optimize_queries")
    workflow.add_edge("optimize_queries", "execute_search")
    workflow.add_edge("execute_search", "evaluate_results")
    
    # Conditional edge
    workflow.add_conditional_edges(
        "evaluate_results",
        should_refine,
        {
            "END": END,
            "REFINE": "refine_query"
        }
    )
    workflow.add_edge("refine_query", "optimize_queries")
    
    return workflow.compile()
```

### Phase 4: Streamlit Integration (app_langgraph.py)
```python
import streamlit as st
from backend.langgraph_orchestrator import build_search_graph

# Build graph once
graph = build_search_graph()

# UI
query = st.text_area("Nhập yêu cầu tìm kiếm...")

if st.button("🚀 Tìm kiếm thông minh"):
    initial_state = {
        "user_query": query,
        "user_preferences": {
            "max_results": max_results,
            "year_range": year_range,
            "sources": selected_sources
        }
    }
    
    # Execute graph
    with st.spinner("AI đang phân tích và tìm kiếm..."):
        final_state = graph.invoke(initial_state)
    
    # Display results
    st.success(f"Tìm thấy {len(final_state['final_results'])} bài báo")
    st.info(f"Quality Score: {final_state['quality_score']:.2f}")
    
    # Show strategy used
    with st.expander("🧠 Chiến lược AI đã dùng"):
        st.json(final_state["search_strategy"])
    
    # Display articles
    for article in final_state["final_results"]:
        display_article(article)
```

---

## 📊 Advantages của LangGraph Approach

### So với App hiện tại:

| Feature | App hiện tại | App LangGraph |
|---------|-------------|---------------|
| **Query optimization** | Manual (user chọn) | Auto (AI quyết định) |
| **Source selection** | Fixed | Dynamic (dựa trên topic) |
| **Error handling** | Simple | Self-healing (auto refine) |
| **Result quality** | No validation | AI evaluation |
| **Parallel execution** | Sequential | True async parallel |
| **Adaptability** | Static | Self-improving |
| **User experience** | Multi-step | One-click |

---

## 🎯 Use Cases

### Case 1: Medical Research
```
Input: "Điều trị ung thư phổi giai đoạn muộn"

LangGraph Flow:
1. Analyze → topic=medical, intent=treatment
2. Plan → Priority: PubMed > Semantic > Scopus
3. Optimize → PubMed: MeSH terms + RCT filter
4. Execute → 45 results
5. Evaluate → Score 0.85 → Good → END
```

### Case 2: Engineering + Vietnamese
```
Input: "Machine learning trong dự báo thời tiết"

LangGraph Flow:
1. Analyze → topic=engineering, language=vi
2. Plan → Semantic Scholar (vì tiếng Việt) + Scopus
3. Optimize → Keep Vietnamese for Semantic
4. Execute → 12 results
5. Evaluate → Score 0.45 → Low → REFINE
6. Refine → Expand to "machine learning weather forecasting climate"
7. Execute → 78 results
8. Evaluate → Score 0.82 → Good → END
```

---

## 🚀 Next Steps

1. **Phase 1 (Week 1):** 
   - Setup LangGraph
   - Build basic nodes (analyze, plan, optimize)
   - Test with mock data

2. **Phase 2 (Week 2):**
   - Implement async API wrappers
   - Build execute & evaluate nodes
   - Test end-to-end flow

3. **Phase 3 (Week 3):**
   - Add refinement loop
   - Build Streamlit UI (app_langgraph.py)
   - A/B test vs current app

4. **Phase 4 (Week 4):**
   - Fine-tune prompts
   - Add caching & optimization
   - Deploy & monitor

---

## 💡 Advanced Features (Future)

1. **Multi-agent collaboration:**
   - Specialist agents cho từng nguồn (PubMedAgent, ScopusAgent)
   - Coordinator agent điều phối

2. **Learning from user feedback:**
   - Thu thập user ratings
   - Fine-tune strategy prompts

3. **Citation network analysis:**
   - Tìm papers liên quan qua citations
   - Build knowledge graph

4. **Multi-turn conversation:**
   - User hỏi thêm: "Tìm bài mới hơn"
   - Agent nhớ context và refine

---

**Tài liệu tham khảo:**
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Multi-agent patterns: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/
