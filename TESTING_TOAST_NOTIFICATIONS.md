# Testing Toast Notifications - Quick Guide

## How to Test

### 1. Start the Application

```bash
cd D:\OneDrive\python\academic_y_van\tim_y_van_04_api
streamlit run app_langgraph.py
```

### 2. Prepare Test Query

Use a medical query to test all features:

```
hãy tìm bài báo tiếng Anh cho chủ đề dùng trí thông minh nhân tạo trong chẩn đoán vết thương
```

Or in English:
```
artificial intelligence in wound diagnosis and treatment
```

### 3. Configure Settings

In the sidebar:
- ✅ Enable PubMed
- ✅ Enable Semantic Scholar
- Set max results: 30-50 (to test filtering)
- Year range: 2020-2025

### 4. Expected Toast Sequence

Watch for these toasts appearing in the **top-right corner**:

#### Normal Flow (No Refinement)
1. 🔍 **Phân tích Query**: medical (en) *(~1-2 seconds)*
2. 📋 **Lập Chiến lược**: 2 nguồn *(~1 second)*
3. ⚙️ **Tối ưu Query** *(~2-3 seconds)*
4. 🚀 **Tìm kiếm Dữ liệu**: Tìm được 47 bài báo *(~5-10 seconds)*
5. 📊 **Đánh giá & Lọc**: 23 bài chất lượng cao (⭐7.8/10) *(~10-20 seconds with AI)*
6. 📝 **Tổng hợp Kết quả**: 23 bài báo *(~5-10 seconds)*
7. ✅ **Hoàn thành tìm kiếm!**

**Total time**: ~25-50 seconds depending on API response times

#### With Refinement Flow
If initial results are poor (< 50% of target):
1. 🔍 **Phân tích Query**: biology (en)
2. 📋 **Lập Chiến lược**: 2 nguồn
3. ⚙️ **Tối ưu Query**
4. 🚀 **Tìm kiếm Dữ liệu**: Tìm được 12 bài báo
5. 📊 **Đánh giá & Lọc**: 5 bài chất lượng cao (⭐6.2/10)
6. 🔄 **Tinh chỉnh Query**: Lần 1/2 ⬅️ **REFINEMENT**
7. ⚙️ **Tối ưu Query** (again)
8. 🚀 **Tìm kiếm Dữ liệu**: Tìm được 28 bài báo
9. 📊 **Đánh giá & Lọc**: 18 bài chất lượng cao (⭐7.5/10)
10. 📝 **Tổng hợp Kết quả**: 18 bài báo
11. ✅ **Hoàn thành tìm kiếm!**

### 5. Verify Toast Content

Check that each toast shows relevant information:

| Node | What to Verify |
|------|----------------|
| 🔍 Phân tích | Topic matches query (medical/engineering/etc) |
| 📋 Lập Chiến lược | Number of sources matches your settings |
| 🚀 Tìm kiếm | Total count > 0 |
| 📊 Đánh giá | Filtered count ≤ total, score between 0-10 |
| 🔄 Tinh chỉnh | Shows attempt 1/2 or 2/2 |
| 📝 Tổng hợp | Count matches filtered results |

### 6. Test Error Handling

To test error toast:

1. **Invalid API Key**: Remove GEMINI_API_KEY from .env
   - Expected: ❌ Toast: "Lỗi: API key required..."

2. **No Sources Selected**: Uncheck all sources in sidebar
   - Expected: ❌ Error message (not a crash)

3. **Network Error**: Disconnect internet during search
   - Expected: ❌ Toast: "Lỗi: Connection timeout..."

## What Success Looks Like

### ✅ Good Signs
- Toasts appear sequentially, not all at once
- Each toast shows relevant data (not "N/A")
- Toast icons match the step type
- Final success toast appears
- Results display correctly in main UI
- No Python errors in terminal

### ❌ Red Flags
- No toasts appear (callback not working)
- Toasts show "N/A" or empty data
- Toasts appear all at once (not streaming)
- Python exceptions in console
- UI freezes during search

## Debugging

### If toasts don't appear:

1. **Check console output**:
   ```bash
   # Should see:
   📍 Node: analyze_query
   📍 Node: plan_strategy
   ...
   ```

2. **Verify callback is being called**:
   Add print statement in `show_progress()`:
   ```python
   def show_progress(node_name: str, node_state: dict):
       print(f"DEBUG: Toast for {node_name}")  # Add this
       ...
   ```

3. **Check state data**:
   Print node_state to see if data is available:
   ```python
   print(f"DEBUG State: {node_state.keys()}")
   ```

### If streaming fails:

The system falls back to regular invoke without toasts. Check:
- Is `progress_callback` parameter passed correctly?
- Does `graph.stream()` work with your LangGraph version?
- Check LangGraph version: `pip show langgraph`

## Performance Monitoring

Watch these metrics during testing:

1. **Toast Timing**: Each toast should appear within 1-20s of previous
2. **Total Duration**: Complete workflow should finish in < 2 minutes
3. **Memory**: No memory leaks (check Task Manager)
4. **CPU**: Reasonable CPU usage (not 100% constantly)

## Browser Compatibility

Test in:
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Firefox
- ⚠️ Safari (Streamlit may have issues)

## Test Cases

### Test Case 1: Medical Query (High Quality)
```
Query: "machine learning in cancer diagnosis 2023"
Expected:
- Topic: medical
- Language: en
- Found: 40-60 articles
- Filtered: 20-30 articles (≥50%)
- Score: ≥ 7.0
- Refinement: 0 (not needed)
```

### Test Case 2: Broad Query (May Need Refinement)
```
Query: "AI applications"
Expected:
- Topic: computer_science
- Language: en
- Found: 10-20 articles
- Filtered: 3-8 articles (< 50%)
- Refinement: 1-2 attempts
- Final score: ≥ 6.0
```

### Test Case 3: Vietnamese Query
```
Query: "trí tuệ nhân tạo trong y học"
Expected:
- Topic: medical
- Language: vi or mixed
- Found: varies
- Translated query used in search
```

## Success Criteria

- [x] All toasts appear in correct order
- [x] Toast messages are informative and accurate
- [x] Icons match the step type
- [x] No errors in console
- [x] Results display correctly
- [x] Refinement loop works (if triggered)
- [x] Final success toast appears
- [x] User can still interact with UI during search

## Next Steps After Testing

If all tests pass:
1. ✅ Mark this feature as production-ready
2. 📝 Update user documentation
3. 🎥 Create demo video/screenshots
4. 🚀 Deploy to production

If tests fail:
1. Check the debugging section above
2. Review console logs
3. Verify API keys are valid
4. Check LangGraph version compatibility
