# ⚡ Research Agent Upgrade - Quick Implementation Guide

> **Mục tiêu:** Nâng cấp từ "Search Tool" → "Research Agent" với AI filtering & synthesis
>
> **Chi tiết đầy đủ:** Xem [RESEARCH_AGENT_UPGRADE_PLAN.md](RESEARCH_AGENT_UPGRADE_PLAN.md)

---

## 🎯 TL;DR - What's Changing?

### Before (Current)
```
Search → Deduplicate → Sample 3 titles → Score → Return ALL results
```
**Problem:** Trả về 40 bài, trong đó có 20 bài không liên quan

### After (Upgraded)
```
Search → Deduplicate → AI reads ALL abstracts → Filter by relevance → Synthesize → Return QUALITY results
```
**Benefit:** Trả về 25 bài chất lượng cao + AI tổng hợp nghiên cứu

---

## 📋 Implementation Checklist

### Phase 1: Core Changes (2-3 days)

- [ ] **Task 1:** Update `backend/state_schema.py`
  ```python
  # Add to SearchState:
  'filtered_results': List[Dict]
  'discarded_articles': List[Dict]
  'synthesis_summary': str
  'filter_statistics': Dict
  ```

- [ ] **Task 2:** Refactor `backend/nodes/evaluate.py`
  - Replace: Sample 3 titles logic
  - Add: Loop through ALL articles
  - Add: Call Gemini to score each abstract (1-10)
  - Add: Keep only score >= 7
  - Update: `quality_score = kept_count / total_count`

- [ ] **Task 3:** Update `backend/langgraph_orchestrator.py`
  ```python
  # In should_refine():
  # OLD: if quality_score >= 0.7: return "end"
  # NEW: if kept_count >= (target * 0.5): return "end"
  ```

### Phase 2: Synthesis (1-2 days)

- [ ] **Task 4:** Create `backend/nodes/synthesize.py`
  - Input: filtered_results (list of high-quality papers)
  - Process: Send abstracts to Gemini
  - Prompt: "Write 300-word literature review answering: {user_query}"
  - Output: state['synthesis_summary']

- [ ] **Task 5:** Integrate synthesis into workflow
  ```python
  # In langgraph_orchestrator.py:
  workflow.add_node("synthesize_findings", ...)
  workflow.add_edge("evaluate_results", "synthesize_findings")
  workflow.add_edge("synthesize_findings", END)
  ```

### Phase 3: UI Updates (1 day)

- [ ] **Task 6:** Update `app_langgraph.py`
  - Add: Synthesis display section (before articles)
  - Add: "Discarded" tab in results
  - Add: Filter statistics in metrics row
  - Update: Show relevance scores on each article

---

## 🔧 Key Code Snippets

### 1. AI Filter Prompt (for evaluate.py)

```python
def create_filter_prompt(user_query, article):
    return f"""You are an expert research paper reviewer.

USER QUERY: "{user_query}"

PAPER:
Title: {article['title']}
Abstract: {article.get('abstract', 'N/A')}
Year: {article['year']}

TASK: Score this paper's relevance to the query (1-10 scale).
- 8-10: Highly relevant, directly addresses query
- 5-7: Moderately relevant, related but not focused
- 1-4: Low relevance, tangential or off-topic

OUTPUT (JSON):
{{
  "score": <1-10>,
  "keep": <true if score >= 7>,
  "reasoning": "<why this score?>"
}}
"""
```

### 2. Filter Logic (evaluate.py core)

```python
def evaluate_results(state, gemini, async_apis):
    articles = state['search_results']
    kept = []
    discarded = []

    # Process each article
    for article in articles:
        # Build prompt
        prompt = create_filter_prompt(state['user_query'], article)

        # Get AI judgment
        response = gemini.evaluate_relevance(prompt)
        result = json.loads(response)

        # Categorize
        article['relevance_score'] = result['score']
        article['discard_reason'] = result['reasoning']

        if result['keep']:
            kept.append(article)
        else:
            discarded.append(article)

    # Update state
    state['final_results'] = kept
    state['discarded_articles'] = discarded
    state['quality_score'] = len(kept) / len(articles)
    state['needs_refinement'] = len(kept) < (state['user_preferences']['max_results'] * 0.5)

    return state
```

### 3. Synthesis Prompt (synthesize.py)

```python
def create_synthesis_prompt(user_query, papers):
    papers_text = "\n\n".join([
        f"[{i+1}] {p['title']} ({p['year']})\n{p['abstract']}"
        for i, p in enumerate(papers)
    ])

    return f"""Write a comprehensive literature review (300-500 words) answering this query:

QUERY: "{user_query}"

Based on these {len(papers)} research papers:

{papers_text}

Your review should:
1. Directly answer the query
2. Summarize key findings
3. Note trends or patterns
4. Cite papers as [1], [2], etc.

Use markdown formatting. Be concise but thorough.
"""
```

### 4. UI Synthesis Display (app_langgraph.py)

```python
# After search completes, before article list:
if st.session_state.langgraph_results:
    synthesis = st.session_state.langgraph_results.get('synthesis_summary')

    if synthesis:
        st.markdown("## 🧠 AI Research Summary")
        with st.expander("📖 Click to read AI-generated literature review", expanded=True):
            st.markdown(synthesis)

            stats = st.session_state.langgraph_results.get('filter_statistics', {})
            st.info(f"📊 Based on {stats.get('kept_count', 0)} highly relevant papers "
                   f"(filtered from {stats.get('total_found', 0)} results)")
```

---

## 🧪 Test Command

After implementing, test with this query:

```python
# In Python terminal or notebook:
from backend.langgraph_orchestrator import build_search_graph, invoke_search

graph = build_search_graph(
    gemini_api_key="your_key",
    pubmed_key="your_key"
)

result = invoke_search(
    graph,
    user_query="AI for cancer diagnosis using medical imaging",
    user_preferences={
        'max_results': 20,
        'year_range': [2020, 2024],
        'sources': ['PubMed', 'Semantic Scholar']
    }
)

# Check results:
print(f"Found: {len(result['search_results'])} total")
print(f"Kept: {len(result['final_results'])} after filtering")
print(f"Discarded: {len(result['discarded_articles'])}")
print(f"\nSynthesis:\n{result['synthesis_summary']}")
```

**Expected output:**
- Found: ~40 papers
- Kept: ~20-25 papers (score >= 7)
- Discarded: ~15-20 papers with reasons
- Synthesis: 300-word coherent summary

---

## ⚠️ Common Pitfalls

### 1. Token Limit Errors
**Problem:** Sending 50 abstracts × 300 words = too many tokens

**Solution:**
```python
# In evaluate.py, process in batches:
BATCH_SIZE = 5
for i in range(0, len(articles), BATCH_SIZE):
    batch = articles[i:i+BATCH_SIZE]
    # Process batch...
```

### 2. Missing Abstracts
**Problem:** Some papers don't have abstracts

**Solution:**
```python
abstract = article.get('abstract', 'N/A')
if abstract == 'N/A':
    # Fall back to title-only scoring
    prompt = create_title_only_prompt(user_query, article)
```

### 3. JSON Parse Errors
**Problem:** Gemini sometimes returns malformed JSON

**Solution:**
```python
try:
    result = json.loads(response)
except json.JSONDecodeError:
    # Retry with simpler prompt or assign default score
    result = {'score': 5, 'keep': True, 'reasoning': 'Parse error - default keep'}
```

---

## 📊 Success Criteria

After implementation, verify:

- [ ] ✅ Filter runs on 100% of articles (not just 3 samples)
- [ ] ✅ At least 60% of results have relevance score >= 7
- [ ] ✅ Discarded articles tab shows clear reasons
- [ ] ✅ Synthesis is coherent and cites papers
- [ ] ✅ Refinement triggers only when < 50% quality papers found
- [ ] ✅ Total workflow time < 30 seconds
- [ ] ✅ No crashes on edge cases (missing abstracts, API errors)

---

## 🚀 Deployment Steps

1. **Test locally** with the test command above
2. **Review discarded papers** manually for first 5 queries to tune threshold
3. **Adjust score threshold** if needed (currently >= 7, maybe change to >= 6)
4. **Update .env** if using new Gemini features
5. **Deploy to Streamlit Cloud** following `DEPLOYMENT.md`
6. **Monitor costs** (filtering uses more API calls)

---

## 📞 Need Help?

- **Detailed plan:** [RESEARCH_AGENT_UPGRADE_PLAN.md](RESEARCH_AGENT_UPGRADE_PLAN.md)
- **Current code:** Check `backend/nodes/evaluate.py:73-120`
- **Architecture:** See `docs/LANGGRAPH_README.md`

---

**Last updated:** 2025-01-27
**Estimated effort:** 2-3 days
**Priority:** HIGH

**Ready to start? Begin with Task 1 (update state schema)!** ✅
