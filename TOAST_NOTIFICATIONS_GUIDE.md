# Toast Notifications Implementation Guide

## Overview
Added real-time visual feedback using `st.toast()` to show the LangGraph agent's progress during search execution.

## Changes Made

### 1. Backend: `backend/langgraph_orchestrator.py`

#### Modified `invoke_search()` function:
- Added `progress_callback` parameter for custom progress tracking
- Implemented streaming using `graph.stream()` instead of `graph.invoke()` when callback is provided
- Callback is called for each node execution with node name and current state

```python
def invoke_search(graph, user_query: str, user_preferences: dict, progress_callback=None):
    # ...
    if progress_callback:
        for event in graph.stream(initial_state):
            for node_name, node_state in event.items():
                progress_callback(node_name, node_state)
        final_state = node_state
    else:
        final_state = graph.invoke(initial_state)
    # ...
```

### 2. Frontend: `app_langgraph.py`

#### Added toast notifications with rich context:

**Node Information Mapping:**
```python
node_info = {
    'analyze_query': {'icon': '🔍', 'name': 'Phân tích Query'},
    'plan_strategy': {'icon': '📋', 'name': 'Lập Chiến lược'},
    'optimize_queries': {'icon': '⚙️', 'name': 'Tối ưu Query'},
    'execute_search': {'icon': '🚀', 'name': 'Tìm kiếm Dữ liệu'},
    'evaluate_results': {'icon': '📊', 'name': 'Đánh giá & Lọc'},
    'refine_query': {'icon': '🔄', 'name': 'Tinh chỉnh Query'},
    'synthesize_findings': {'icon': '📝', 'name': 'Tổng hợp Kết quả'}
}
```

**Progress Callback Function:**
- `analyze_query`: Shows detected topic and language
- `plan_strategy`: Shows number of sources selected
- `execute_search`: Shows total articles found
- `evaluate_results`: Shows filtered count and average quality score
- `refine_query`: Shows refinement attempt number
- `synthesize_findings`: Shows number of papers synthesized

## User Experience

### What Users Will See:

1. **🔍 Phân tích Query**: medical (en)
   - Shows the detected topic and language

2. **📋 Lập Chiến lược**: 2 nguồn
   - Shows how many sources will be searched

3. **⚙️ Tối ưu Query**
   - Query optimization in progress

4. **🚀 Tìm kiếm Dữ liệu**: Tìm được 47 bài báo
   - Shows total raw results found

5. **📊 Đánh giá & Lọc**: 23 bài chất lượng cao (⭐7.8/10)
   - Shows filtered count and average relevance score

6. **🔄 Tinh chỉnh Query**: Lần 1/2 (if refinement needed)
   - Shows refinement attempt number

7. **📝 Tổng hợp Kết quả**: 23 bài báo
   - Final synthesis count

8. **✅ Hoàn thành tìm kiếm!**
   - Completion notification

## Benefits

1. **Transparency**: Users see exactly what the AI is doing at each step
2. **Progress Feedback**: Real-time updates prevent user anxiety during long searches
3. **Quality Metrics**: Users see relevance scores and filtering results
4. **Debugging**: Easier to identify which step takes long or fails
5. **Professional UX**: Modern toast notifications enhance user experience

## Testing

To test the implementation:

```bash
streamlit run app_langgraph.py
```

Then perform a search and watch the toast notifications appear in the top-right corner as each node executes.

## Technical Notes

- Toast notifications are non-blocking and auto-dismiss after a few seconds
- Each toast includes an icon matching the node type
- Messages are concise but informative
- Fallback to regular invoke if no callback provided (backward compatible)

## Future Enhancements

Possible improvements:
- Add timing information (e.g., "Completed in 2.3s")
- Color-coded toasts (success=green, refinement=yellow, error=red)
- Progress bar integration
- Detailed error messages in toasts
- User preference to disable toast notifications
