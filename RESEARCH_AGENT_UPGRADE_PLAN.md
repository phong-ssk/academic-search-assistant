# 🚀 Research Agent Upgrade Plan

**Objective:** Transform the current "Smart Search Tool" into a true "Research Agent" with AI-powered filtering, ranking, and synthesis capabilities.

**Status:** 📋 Planning Phase
**Priority:** HIGH
**Estimated Effort:** 2-3 days
**Last Updated:** 2025-01-27

---

## 📊 Current State Analysis

### Identified Gaps

#### 1. **Superficial Evaluation** 🔴 Critical
- **Current behavior:** `evaluate.py` samples only 3 titles from each source
- **Problem:**
  - If 3 sampled articles are good but 47 others are junk → HIGH score (False Positive)
  - If 3 sampled articles are mediocre but others are excellent → Unnecessary refinement
- **Impact:** User receives mixed quality results with many irrelevant papers

#### 2. **No Semantic Filtering** 🟠 High
- **Current behavior:** Only technical deduplication (DOI/Title matching)
- **Problem:**
  - Example: Query "AI for cancer diagnosis" returns:
    - ✅ "Deep learning for lung cancer detection in CT scans" (RELEVANT)
    - ❌ "AI system for managing cancer patient records" (IRRELEVANT - but has keywords)
- **Impact:** 30-50% of results may be tangentially related but not useful

#### 3. **Wasted Abstract Data** 🟡 Medium
- **Current behavior:** Abstracts fetched but only shown in UI
- **Problem:** Abstracts contain 80% of paper's value, unused by AI
- **Impact:** Missing opportunity for intelligent filtering and synthesis

---

## 🎯 Proposed Solution: Funnel Filtering Pipeline

### New Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRENT WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│  SEARCH (50 papers)                                         │
│     ↓                                                        │
│  DEDUPLICATE (40 papers)                                    │
│     ↓                                                        │
│  EVALUATE (sample 3 titles → quality_score)                 │
│     ↓                                                        │
│  Decision: quality < 0.7? → REFINE or STOP                  │
│     ↓                                                        │
│  RETURN ALL 40 PAPERS (mixed quality)                       │
└─────────────────────────────────────────────────────────────┘

                            ⬇⬇⬇ UPGRADE ⬇⬇⬇

┌─────────────────────────────────────────────────────────────┐
│                     NEW WORKFLOW                            │
├─────────────────────────────────────────────────────────────┤
│  SEARCH (50 papers)                                         │
│     ↓                                                        │
│  DEDUPLICATE (40 papers)                                    │
│     ↓                                                        │
│  🆕 AI FILTER & RANK (read ALL abstracts)                   │
│     ├─ Score each paper 1-10 for relevance                  │
│     ├─ Keep papers with score >= 7                          │
│     └─ Store discarded papers + reasons                     │
│     ↓                                                        │
│  FILTERED RESULTS (25 high-quality papers)                  │
│     ↓                                                        │
│  Decision: count < 50% of target? → REFINE or CONTINUE      │
│     ↓                                                        │
│  🆕 SYNTHESIZE (AI reads abstracts → write review)          │
│     ↓                                                        │
│  RETURN: 25 papers + AI synthesis + discarded list          │
└─────────────────────────────────────────────────────────────┘
```

### Key Improvements

1. **AI Filter & Rank Node** - Reads EVERY abstract, scores relevance
2. **Math-based Stopping** - Refine only if insufficient quality papers found
3. **Synthesis Node** - AI writes mini literature review from abstracts
4. **Transparency** - Show discarded papers so users can verify AI decisions

---

## 📋 Implementation Roadmap

### Phase 1: Foundation (Priority: HIGH)

#### Task 1.1: Update State Schema
**File:** `backend/state_schema.py`

**Changes needed:**
```python
# Add these fields to SearchState TypedDict:

'filtered_results': List[Dict]        # Papers that passed AI filter
'discarded_articles': List[Dict]      # Papers rejected + reasons
'relevance_scores': Dict[str, float]  # Paper ID → score mapping
'synthesis_summary': str              # AI-generated literature review
'filter_statistics': Dict             # Stats: total, kept, discarded, avg_score
```

**Rationale:** Need to track filtering process for transparency and debugging.

---

#### Task 1.2: Design AI Filter Prompt
**File:** New file `backend/prompts/filter_prompt.py` (recommended for maintainability)

**Prompt Template:**
```
ROLE: You are an expert academic literature reviewer.

CONTEXT:
User Query: "{user_query}"
Research Topic: {topic_analysis}

TASK: Evaluate the relevance of the following research paper to the user's query.

PAPER DETAILS:
- Title: {title}
- Abstract: {abstract}
- Journal: {journal}
- Year: {year}

EVALUATION CRITERIA:
1. Direct relevance to query topic (0-4 points)
2. Methodological appropriateness (0-3 points)
3. Recency and citation impact (0-3 points)

OUTPUT FORMAT (JSON):
{
  "relevance_score": <1-10>,
  "keep": <true/false>,
  "reasoning": "<brief explanation>",
  "key_findings": "<1 sentence summary if relevant>"
}

RULES:
- Score >= 7: High relevance, definitely keep
- Score 4-6: Moderate relevance, keep only if specific niche match
- Score < 4: Low relevance, discard
- Be strict but fair
- Consider both exact and conceptual matches
```

---

### Phase 2: Core Filter Logic (Priority: HIGH)

#### Task 2.1: Refactor evaluate.py
**File:** `backend/nodes/evaluate.py`

**Current function:** `evaluate_results(state, gemini, async_apis)`

**New logic flow:**

```
INPUT: state['search_results'] (deduplicated articles)

STEP 1: Batch Processing
├─ Split articles into batches of 5-10 (avoid token limits)
└─ Process batches sequentially or with controlled concurrency

STEP 2: For each article in batch:
├─ Extract: title, abstract, journal, year, doi/pmid
├─ Build prompt with user_query context
├─ Call Gemini API with filter prompt
└─ Parse JSON response: {score, keep, reasoning, key_findings}

STEP 3: Categorize Results
├─ filtered_results = articles with keep=true
├─ discarded_articles = articles with keep=false + reasoning
└─ relevance_scores = mapping of article_id → score

STEP 4: Calculate Statistics
├─ total_found = len(search_results)
├─ total_kept = len(filtered_results)
├─ total_discarded = len(discarded_articles)
├─ avg_relevance_score = mean of all scores
└─ quality_score = total_kept / total_found (% of useful papers)

STEP 5: Update State
├─ state['final_results'] = filtered_results
├─ state['discarded_articles'] = discarded_articles
├─ state['relevance_scores'] = relevance_scores
├─ state['quality_score'] = quality_score
├─ state['filter_statistics'] = {...}
└─ state['needs_refinement'] = (total_kept < target * 0.5)

OUTPUT: Updated state
```

**Error Handling:**
- If abstract is missing → use title only + note in reasoning
- If Gemini API fails → assign default score 5 (neutral) + log error
- If JSON parse fails → retry with simpler prompt

**Optimization Tips:**
- Cache filter results (same paper might appear in refinement)
- Use batch API calls where possible
- Consider parallel processing with asyncio for speed

---

#### Task 2.2: Update Stopping Condition
**File:** `backend/langgraph_orchestrator.py`

**Function:** `should_refine(state)`

**Current logic:**
```python
needs_refinement = state.get('needs_refinement', False)
quality_score = state.get('quality_score', 0.0)

if quality_score >= 0.7:
    return "end"
```

**New logic:**
```python
needs_refinement = state.get('needs_refinement', False)
filtered_count = len(state.get('final_results', []))
target_count = state['user_preferences']['max_results']
refinement_count = state.get('refinement_count', 0)

# Math-based decision:
sufficient_results = filtered_count >= (target_count * 0.5)
max_attempts_reached = refinement_count >= 2

if sufficient_results or max_attempts_reached:
    print(f"✅ Stopping: {filtered_count} quality papers found")
    return "end"
else:
    print(f"🔄 Refining: only {filtered_count}/{target_count} quality papers")
    return "refine"
```

---

### Phase 3: Synthesis Feature (Priority: MEDIUM)

#### Task 3.1: Create Synthesis Node
**File:** `backend/nodes/synthesize.py` (NEW)

**Function:** `synthesize_findings(state, gemini)`

**Logic:**
```
INPUT: state['final_results'] (filtered high-quality papers)

STEP 1: Prepare Data
├─ Extract abstracts from all filtered papers
├─ Create citation map: {paper_id → [Author, Year, Title]}
└─ Group papers by topic/method if needed (optional clustering)

STEP 2: Build Synthesis Prompt
Context: User query + research topic
Input: List of [ID, Title, Abstract, Year] for each paper
Task: "Write a comprehensive literature review summary (300-500 words) that:
  1. Answers the user's query based on these papers
  2. Identifies key findings and trends
  3. Notes any conflicting results or gaps
  4. Cites sources using [ID] format"

STEP 3: Call Gemini
├─ Send prompt to Gemini with high token limit (2000+)
├─ Parse response
└─ Handle errors gracefully

STEP 4: Format Output
├─ Add section headers (Key Findings, Trends, Gaps, etc.)
├─ Convert [ID] citations to clickable links in UI
└─ Add metadata: synthesis_date, papers_count, avg_year

STEP 5: Update State
state['synthesis_summary'] = formatted_synthesis
state['synthesis_metadata'] = {...}

OUTPUT: Updated state
```

**Synthesis Prompt Template:**
```
ROLE: You are an expert research synthesizer.

TASK: Write a comprehensive literature review summary based on the following {count} papers.

USER QUERY: "{user_query}"

PAPERS:
{for each paper:
  [ID{i}] {title} ({year})
  Abstract: {abstract}
}

INSTRUCTIONS:
1. ANSWER THE QUERY: Directly address what the user asked
2. KEY FINDINGS: Summarize main discoveries/conclusions across papers
3. METHODOLOGICAL TRENDS: Note common approaches (if applicable)
4. CONFLICTING RESULTS: Highlight any disagreements between studies
5. RESEARCH GAPS: Identify what's missing or needs more study
6. CITATIONS: Reference papers as [ID1], [ID2], etc.

FORMAT:
- Use markdown
- 300-500 words
- Professional academic tone
- Be concise but comprehensive

OUTPUT: Your literature review summary
```

---

#### Task 3.2: Integrate Synthesis into Workflow
**File:** `backend/langgraph_orchestrator.py`

**Changes:**
```python
# Add synthesis node
from .nodes.synthesize import synthesize_findings

workflow.add_node("synthesize_findings",
                  lambda state: synthesize_findings(state, gemini))

# Update workflow edges
# OLD: evaluate → (refine or END)
# NEW: evaluate → (refine or synthesize) → END

workflow.add_conditional_edges(
    "evaluate_results",
    should_refine,
    {
        "refine": "refine_query",
        "continue": "synthesize_findings"  # NEW
    }
)

workflow.add_edge("synthesize_findings", END)
```

---

### Phase 4: UI/UX Enhancements (Priority: MEDIUM)

#### Task 4.1: Add Synthesis Display
**File:** `app_langgraph.py`

**Location:** After search results header, before article list

**New section:**
```python
# Display AI Synthesis (if available)
if st.session_state.langgraph_results:
    synthesis = st.session_state.langgraph_results.get('synthesis_summary')

    if synthesis:
        st.markdown("### 🧠 AI Literature Review")
        with st.expander("📖 Read AI-generated research summary", expanded=True):
            st.markdown(synthesis)

            # Show metadata
            metadata = st.session_state.langgraph_results.get('synthesis_metadata', {})
            st.caption(f"Based on {metadata.get('papers_count', 0)} papers | "
                      f"Avg publication year: {metadata.get('avg_year', 'N/A')}")
```

---

#### Task 4.2: Add Discarded Articles Tab
**File:** `app_langgraph.py`

**Location:** In results tabs section

**New tab:**
```python
# Current tabs: All, PubMed, Scopus, Semantic Scholar
# Add: Discarded tab

tab1, tab2, tab3, tab4, tab_discarded = st.tabs([
    f"🌍 All ({len(articles)})",
    f"🔬 PubMed ({len(pubmed_articles)})",
    f"📚 Scopus ({len(scopus_articles)})",
    f"🌐 Semantic ({len(semantic_articles)})",
    f"🗑️ Discarded ({len(discarded_articles)})"  # NEW
])

with tab_discarded:
    st.info("Papers filtered out by AI. Review to verify decisions.")

    discarded = final_state.get('discarded_articles', [])

    for i, article in enumerate(discarded, 1):
        with st.container():
            st.markdown(f"**{i}. {article['title']}**")
            st.caption(f"Score: {article.get('relevance_score', 'N/A')}/10")

            # Show AI reasoning
            with st.expander("🤖 Why was this discarded?"):
                st.write(article.get('discard_reason', 'No reason provided'))

            st.markdown("---")
```

---

#### Task 4.3: Add Filter Statistics Display
**File:** `app_langgraph.py`

**Location:** In metrics section

**New metrics:**
```python
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📚 Total Found", metadata.get('total_found', 0))

with col2:
    st.metric("✅ Kept", len(final_results),
              delta=f"{(len(final_results)/metadata.get('total_found', 1)*100):.0f}%")

with col3:
    st.metric("🗑️ Filtered",
              metadata.get('total_found', 0) - len(final_results))

with col4:
    avg_score = final_state.get('filter_statistics', {}).get('avg_score', 0)
    st.metric("⭐ Avg Score", f"{avg_score:.1f}/10")

with col5:
    st.metric("🔄 Refinements", refinement_count)
```

---

## 🧪 Testing Strategy

### Test Case 1: Medical Query (Vietnamese)
```
Query: "Điều trị tăng huyết áp ở người cao tuổi bằng thuốc mới"

Expected Behavior:
1. Search finds 40 papers (after dedup)
2. AI Filter:
   - KEEP (score 8-10): Papers about new antihypertensive drugs in elderly
   - DISCARD (score < 7): Papers about:
     - Hypertension in young adults
     - Non-pharmacological treatments only
     - Management systems (not treatment)
3. Refined results: ~20-25 highly relevant papers
4. Synthesis: 300-word review answering "What are the new drugs and their efficacy?"
5. No refinement needed (sufficient results)
```

### Test Case 2: Broad Engineering Query
```
Query: "Machine learning"

Expected Behavior:
1. Search finds 50 papers (too broad)
2. AI Filter:
   - Many papers get 5-6 scores (moderately relevant but vague)
   - Only 8 papers score >= 7
3. Trigger Refinement (8 < 50*0.5)
4. Refined query: "machine learning applications [specific domain from user context]"
5. Second search: 35 papers → 18 kept
6. Synthesis generated
7. Stop (sufficient results)
```

### Test Case 3: Edge Case - No Abstracts
```
Setup: Force some papers to have missing abstracts

Expected Behavior:
1. Filter function detects missing abstract
2. Falls back to title-only scoring
3. Adds note in discard_reason: "Limited data (no abstract)"
4. Lower confidence scores for these papers
5. Process continues without crashing
```

---

## 📊 Success Metrics

### Quantitative
- **Relevance Improvement:**
  - Before: User satisfaction ~60% (estimated)
  - After: Target >85% (validate with user feedback)

- **Precision:**
  - Before: ~50% of results are highly relevant
  - After: >80% of final_results are highly relevant (score >= 7)

- **Efficiency:**
  - Reduce refinement cycles by 30% (better first-time results)
  - Synthesis saves users 15-30 min of reading time

### Qualitative
- Users can quickly understand research landscape (via synthesis)
- Transparency builds trust (users can check discarded papers)
- Fewer complaints about irrelevant results

---

## ⚠️ Risks & Mitigation

### Risk 1: Token Cost Explosion
**Problem:** Filtering 50 abstracts × 300 tokens each = 15K tokens/search

**Mitigation:**
- Use Gemini Flash (cheaper model) for filtering
- Batch processing to reduce API calls
- Cache filter results
- Limit abstracts to first 250 words if too long

### Risk 2: AI Filter Too Strict
**Problem:** Might discard good papers due to overly strict scoring

**Mitigation:**
- Tune threshold (maybe 6 instead of 7)
- A/B test with user feedback
- Show discarded papers so users can override
- Add "rescue" button to move discarded → kept

### Risk 3: Synthesis Quality
**Problem:** AI might generate generic summaries

**Mitigation:**
- Provide detailed prompt with examples
- Require specific citations
- Validate synthesis has >70% unique content (not just copy abstract)
- Human review of first 10 syntheses

### Risk 4: Performance Degradation
**Problem:** Extra AI calls slow down workflow

**Mitigation:**
- Parallel processing where possible
- Show progress bars ("Filtering paper 10/40...")
- Offer "Quick mode" (skip synthesis) vs "Deep mode" (full workflow)

---

## 📅 Implementation Timeline

### Week 1: Core Filtering
- **Days 1-2:** Update schema + design prompts
- **Days 3-4:** Implement filter logic in evaluate.py
- **Day 5:** Update stopping conditions + test

### Week 2: Synthesis & UI
- **Days 1-2:** Create synthesis node
- **Days 3-4:** Update UI with new tabs and displays
- **Day 5:** Integration testing + bug fixes

### Week 3: Polish & Deploy
- **Days 1-2:** User testing + feedback
- **Days 3-4:** Optimize performance + costs
- **Day 5:** Deploy to production

---

## 🎯 Next Steps

1. **Review & Approve** this plan with stakeholders
2. **Prioritize** features (can defer synthesis to Phase 2 if needed)
3. **Set up** experiment tracking (log filter decisions for analysis)
4. **Start** with Task 1.1 (update schema)
5. **Iterate** based on test results

---

## 📚 References

### Related Files
- Current evaluation: `backend/nodes/evaluate.py:73-120`
- State schema: `backend/state_schema.py`
- Orchestrator: `backend/langgraph_orchestrator.py:18-48`
- UI: `app_langgraph.py:356-524`

### Documentation
- See `docs/LANGGRAPH_README.md` for workflow architecture
- See `docs/FINAL_SUMMARY.md` for current system design

---

**Status:** 📋 Ready for Implementation
**Assigned to:** Development Team
**Review by:** 2025-02-03

---

*This document is a living plan and will be updated as implementation progresses.*
