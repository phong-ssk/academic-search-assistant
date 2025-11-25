# 🧠 LangGraph Academic Search - README

## 📋 Tổng quan

Hệ thống tìm kiếm y văn thông minh sử dụng **LangGraph** để orchestrate workflow AI tự động.

## 🎯 Tính năng chính

### 1. **Tự động phân tích Query** (Analyze Node)
- Nhận diện topic: medical, engineering, computer_science, social_science
- Xác định intent: review, clinical_trial, case_study, meta_analysis
- Detect language: Vietnamese, English, Mixed
- Extract keywords & MeSH terms

### 2. **Tự động lập Chiến lược** (Plan Node)
- Chọn nguồn tối ưu dựa trên topic
- Quyết định filters (năm, số lượng)
- Priority: PubMed > Scopus > Semantic Scholar

### 3. **Tối ưu Query cho từng nguồn** (Optimize Node)
- **PubMed**: MeSH terms + Boolean operators
- **Scopus**: TITLE-ABS-KEY() syntax
- **Semantic Scholar**: Natural language (giữ tiếng Việt)

### 4. **Tìm kiếm Song song** (Execute Node)
- Async parallel search
- Cache 30 phút TTL
- Timeout 60s per source

### 5. **Đánh giá & Loại trùng** (Evaluate Node)
- Quality score 0.0-1.0
- Deduplication: DOI → PMID → Title similarity (85%)
- Early stopping nếu đủ kết quả

### 6. **Auto Refinement** (Refine Node)
- Tự động cải thiện query nếu quality < 0.7
- Max 2 lần refinement
- Mở rộng year range, tăng max results

## 🛑 Điều kiện DỪNG tìm kiếm

1. ✅ **Quality score >= 0.7**
2. ✅ **Tìm được >= 80%** số lượng mong muốn
3. ✅ **Đã refine 2 lần**

## 🗑️ Cơ chế Deduplication

### Priority loại trùng:
1. **DOI** (highest priority) - Standard identifier
2. **PMID** (PubMed ID) - Cross-reference với Scopus
3. **Title Similarity** (fallback) - Jaccard 85%

### Ví dụ:
```
Input: 100 articles (PubMed: 40, Scopus: 35, Semantic: 25)
- 15 trùng DOI
- 5 trùng PMID
- 3 trùng Title
→ Output: 77 unique articles
```

## 💾 Cơ chế Cache

- **TTL**: 30 phút
- **Key**: MD5(source + query + params)
- **Storage**: In-memory dictionary
- **Benefit**: Tránh gọi API lại cho cùng query

## 🚀 Sử dụng

### Chạy App LangGraph:
```bash
streamlit run app_langgraph.py
```

### So sánh với App cũ:
```bash
# App cũ (manual)
streamlit run app.py

# App mới (LangGraph AI)
streamlit run app_langgraph.py
```

## 📊 Workflow Flow

```
START
  ↓
ANALYZE (phân tích query)
  ↓
PLAN (lập chiến lược)
  ↓
OPTIMIZE (tối ưu queries)
  ↓
EXECUTE (tìm kiếm song song)
  ↓
EVALUATE (đánh giá & loại trùng)
  ↓
[Quality OK?]
  ├─ YES → END
  └─ NO → REFINE → quay lại OPTIMIZE (max 2 lần)
```

## 🔧 Configuration

### Environment Variables (.env):
```bash
GEMINI_API_KEY=your_gemini_key
PUBMED_API_KEY=your_pubmed_key  # Optional
SCOPUS_API_KEY=your_scopus_key  # Optional
SEMANTIC_SCHOLAR_API_KEY=your_semantic_key  # Optional
```

## 📁 Cấu trúc Files

```
backend/
├── async_apis.py           # Async wrappers + Cache + Dedup
├── state_schema.py         # LangGraph State definition
├── langgraph_orchestrator.py  # Build & compile graph
├── nodes/
│   ├── __init__.py
│   ├── analyze.py          # Analyze query
│   ├── plan.py             # Plan strategy
│   ├── optimize.py         # Optimize queries
│   ├── execute.py          # Execute search
│   ├── evaluate.py         # Evaluate results
│   └── refine.py           # Refine query
app_langgraph.py            # Streamlit UI
```

## 🆚 So sánh App cũ vs LangGraph

| Feature | App cũ | App LangGraph |
|---------|--------|---------------|
| **Query optimization** | Manual (user chọn) | Auto AI |
| **Source selection** | Fixed by user | Dynamic (AI chọn) |
| **Deduplication** | Simple DOI check | DOI + PMID + Title |
| **Caching** | ❌ None | ✅ 30min TTL |
| **Parallel search** | Sequential | True async |
| **Auto refinement** | ❌ None | ✅ Max 2 times |
| **Quality check** | ❌ None | ✅ AI evaluation |

## 📈 Performance

- **Average search time**: 5-15s (with cache), 15-30s (first time)
- **Deduplication rate**: ~15-25% removed
- **Cache hit rate**: ~40% (after initial searches)
- **Refinement rate**: ~20% of searches need refinement

## 🎓 Use Cases

### Case 1: Medical Research (Vietnamese)
```
Input: "Điều trị ung thư phổi giai đoạn muộn"
→ Analyze: topic=medical, language=vi
→ Plan: PubMed (priority) + Semantic Scholar
→ Optimize: PubMed với MeSH terms, Semantic giữ tiếng Việt
→ Execute: 45 articles
→ Evaluate: Quality 0.85 → STOP
```

### Case 2: Engineering + English
```
Input: "Machine learning in weather forecasting"
→ Analyze: topic=engineering, language=en
→ Plan: Scopus (priority) + Semantic Scholar
→ Execute: 12 articles (low)
→ Evaluate: Quality 0.45 → REFINE
→ Refine: Expand to "machine learning weather prediction climate"
→ Execute: 78 articles
→ Evaluate: Quality 0.82 → STOP
```

## 🐛 Debugging

### Enable verbose logging:
```python
# In langgraph_orchestrator.py
print(f"State: {json.dumps(state, indent=2)}")
```

### Check cache:
```python
from backend.async_apis import SearchCache
cache = SearchCache()
print(cache.cache.keys())
```

## 📞 Support

Nếu có lỗi, check:
1. ✅ GEMINI_API_KEY có hợp lệ?
2. ✅ Dependencies đã cài đủ?
3. ✅ Internet connection OK?
4. ✅ API rate limits?

## 🔜 Future Improvements

- [ ] Multi-agent collaboration
- [ ] Citation network analysis
- [ ] User feedback learning
- [ ] Multi-turn conversation
- [ ] Export results (PDF, CSV, BibTeX)
