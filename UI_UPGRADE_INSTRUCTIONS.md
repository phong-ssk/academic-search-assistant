# UI Upgrade Instructions for app_langgraph.py

## Changes to Make

### 1. Update Metrics Section (Line 371-389)

**REPLACE:**
```python
# === PHẦN 1: THỐNG KÊ TỔNG QUAN (4 METRICS) ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 Bài báo", len(final_state['final_results']))

with col2:
    quality = final_state['quality_score']
    quality_label = "Xuất sắc" if quality >= 0.8 else "Tốt" if quality >= 0.6 else "Chấp nhận"
    st.metric("⭐ Chất lượng", f"{quality:.2f}", quality_label)

with col3:
    st.metric("🔄 Refinement", f"{final_state['refinement_count']}/2")

with col4:
    metadata = final_state.get('metadata', {})
    removed = metadata.get('total_found', 0) - len(final_state['final_results'])
    st.metric("🗑️ Đã loại", f"{removed}")
```

**WITH:**
```python
# === PHẦN 1: THỐNG KÊ TỔNG QUAN (5 METRICS) - UPDATED ===
col1, col2, col3, col4, col5 = st.columns(5)

# Get filter statistics
filter_stats = final_state.get('filter_statistics', {})
total_found = filter_stats.get('total_found', 0)
kept_count = len(final_state.get('final_results', []))
discarded_count = filter_stats.get('discarded', 0)
avg_score = filter_stats.get('avg_score', 0.0)
pass_rate = filter_stats.get('pass_rate', 0.0)

with col1:
    st.metric("📚 Tổng tìm thấy", total_found)

with col2:
    delta_pct = f"+{pass_rate}%" if pass_rate > 0 else None
    st.metric("✅ Giữ lại", kept_count, delta=delta_pct)

with col3:
    st.metric("🗑️ Lọc ra", discarded_count)

with col4:
    score_label = "Tốt" if avg_score >= 7 else "Trung bình" if avg_score >= 5 else "Thấp"
    st.metric("⭐ Điểm TB", f"{avg_score}/10", score_label)

with col5:
    st.metric("🔄 Refine", f"{final_state['refinement_count']}/2")
```

### 2. Add Literature Synthesis Section (Insert AFTER line 390, BEFORE "Lưu Kết quả")

**INSERT:**
```python
        st.markdown("---")

        # === NEW: PHẦN 2: AI LITERATURE SYNTHESIS ===
        synthesis = final_state.get('synthesis_summary')

        if synthesis:
            st.markdown("## 🧠 AI Literature Review")

            with st.expander("📖 Đọc tổng quan nghiên cứu do AI viết", expanded=True):
                st.markdown(synthesis)

                # Show synthesis metadata
                synth_meta = final_state.get('synthesis_metadata', {})
                papers_count = synth_meta.get('papers_count', 0)
                avg_year = synth_meta.get('avg_year', 'N/A')
                status = synth_meta.get('status', 'unknown')

                col_meta1, col_meta2, col_meta3 = st.columns(3)
                with col_meta1:
                    st.caption(f"📊 Dựa trên {papers_count} bài báo chất lượng cao")
                with col_meta2:
                    if isinstance(avg_year, (int, float)):
                        st.caption(f"📅 Năm TB: {avg_year:.1f}")
                    else:
                        st.caption(f"📅 Năm TB: {avg_year}")
                with col_meta3:
                    status_icon = "✅" if status == "success" else "⚠️"
                    st.caption(f"{status_icon} Status: {status}")

        st.markdown("---")

        # === PHẦN 3: LƯU KẾT QUẢ === (was PHẦN 2)
```

### 3. Update Article Tabs Section (Around line 542-547)

**FIND:**
```python
tab1, tab2, tab3, tab4 = st.tabs([
    f"🌍 Tất cả ({len(articles)})",
    f"🔬 PubMed ({len(pubmed_articles)})",
    f"📚 Scopus ({len(scopus_articles)})",
    f"🌐 Semantic Scholar ({len(semantic_articles)})"
])
```

**REPLACE WITH:**
```python
# Get discarded articles
discarded_articles = final_state.get('discarded_articles', [])

tab1, tab2, tab3, tab4, tab_discarded = st.tabs([
    f"🌍 Tất cả ({len(articles)})",
    f"🔬 PubMed ({len(pubmed_articles)})",
    f"📚 Scopus ({len(scopus_articles)})",
    f"🌐 Semantic Scholar ({len(semantic_articles)})",
    f"🗑️ Bị lọc ({len(discarded_articles)})"  # NEW TAB
])
```

### 4. Add Discarded Tab Content (After tab4 content, around line 633)

**INSERT:**
```python
        with tab_discarded:
            if not discarded_articles:
                st.info("✅ Không có bài báo nào bị lọc - tất cả đều đạt tiêu chuẩn!")
            else:
                st.warning(f"⚠️ {len(discarded_articles)} bài báo không đủ điểm (< 7/10)")
                st.caption("💡 Xem lại các bài này để kiểm tra xem AI có lọc nhầm không")

                for i, article in enumerate(discarded_articles, 1):
                    with st.container():
                        # Title
                        title = article.get('title', 'N/A')
                        st.markdown(f"### {i}. {title}")

                        # Metadata row
                        col_disc1, col_disc2, col_disc3 = st.columns(3)

                        with col_disc1:
                            source = article.get('source', 'N/A')
                            year = article.get('year', 'N/A')
                            st.caption(f"**Nguồn:** {source} | **Năm:** {year}")

                        with col_disc2:
                            score = article.get('relevance_score', 'N/A')
                            if isinstance(score, (int, float)):
                                st.caption(f"**⭐ Điểm:** {score}/10")
                            else:
                                st.caption(f"**⭐ Điểm:** {score}")

                        with col_disc3:
                            # Link to paper
                            link = article.get('link', '#')
                            if link != '#':
                                st.markdown(f"[🔗 Xem bài báo]({link})")

                        # AI Reasoning - why was it discarded?
                        with st.expander("🤖 Tại sao bị lọc?"):
                            reasoning = article.get('discard_reason') or article.get('ai_reasoning', 'Không có lý do')
                            st.write(reasoning)

                        # Abstract (if available)
                        if show_abstract and article.get('abstract', 'N/A') != 'N/A':
                            with st.expander("📄 Xem tóm tắt"):
                                st.markdown(article['abstract'])

                        st.markdown("---")
```

### 5. Update display_article() Function (Around line 549)

**ADD relevance score display to each article:**

Find the caption section (around line 571-579) and ADD:

```python
# After the existing caption parts, add:
if article.get('relevance_score') is not None:
    score = article.get('relevance_score')
    score_icon = "⭐" if score >= 8 else "✨" if score >= 7 else ""
    caption_parts.append(f"{score_icon}**AI Score:** {score}/10")
```

### 6. Update PHẦN 3 Section Numbers

Since we added synthesis as PHẦN 2, update:
- "PHẦN 3: LƯU KẾT QUẢ" → Keep as is (was PHẦN 2)
- "PHẦN 3: CHIẾN LƯỢC AI" → Becomes "PHẦN 4: CHIẾN LƯỢC AI"
- "PHẦN 4: WORKFLOW LOG" → Becomes "PHẦN 5: WORKFLOW LOG"

## Summary of Changes

1. ✅ **Metrics**: 4 columns → 5 columns with filter statistics
2. ✅ **NEW Section**: AI Literature Review synthesis display
3. ✅ **NEW Tab**: Discarded articles tab
4. ✅ **Enhanced Display**: Show relevance scores on articles
5. ✅ **Better UX**: Clear explanations of why papers were filtered

## Testing Checklist

After making these changes:

- [ ] Metrics display correctly with new filter statistics
- [ ] Synthesis section shows when papers are found
- [ ] Synthesis section handles no-papers case
- [ ] Discarded tab shows filtered papers with reasons
- [ ] Discarded tab shows empty state when no papers discarded
- [ ] Relevance scores display on kept articles
- [ ] All tabs work correctly
- [ ] No layout issues or overlapping content

## Notes

- The synthesis will only show if `synthesis_summary` exists in state
- Discarded tab will be empty if all papers passed (score >= 7)
- This is backward compatible - if old state without new fields, it gracefully handles missing data
