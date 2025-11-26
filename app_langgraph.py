"""
Academic Search Assistant - LangGraph Version
Tìm kiếm thông minh với AI orchestration
"""
import streamlit as st
from backend.langgraph_orchestrator import build_search_graph, invoke_search
from backend.project_manager import ProjectManager
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Cấu hình trang
st.set_page_config(
    page_title="🧠 Academic Search - LangGraph AI",
    page_icon="🧠",
    layout="wide"
)

# Load API keys - Try .env first, then fall back to Streamlit secrets
def get_api_key(key_name):
    """Get API key from .env or Streamlit secrets"""
    # Try .env first
    env_value = os.getenv(key_name, "")
    if env_value:
        return env_value

    # Fall back to Streamlit secrets
    try:
        return st.secrets.get(key_name, "")
    except (FileNotFoundError, KeyError):
        return ""

gemini_key = get_api_key("GEMINI_API_KEY")
pubmed_key = get_api_key("PUBMED_API_KEY")
scopus_key = get_api_key("SCOPUS_API_KEY")
semantic_key = get_api_key("SEMANTIC_SCHOLAR_API_KEY")

# --- SIDEBAR ---
with st.sidebar:
    # Project Management Section
    st.header("📂 Quản lý Dự án")
    
    pm = ProjectManager()
    
    # Tab for Projects and Settings
    tab_projects, tab_settings = st.tabs(["Dự án", "Cài đặt"])
    
    with tab_projects:
        # List existing projects
        all_projects = pm.get_all_projects()
        
        if all_projects:
            st.markdown("### 📚 Dự án hiện có")
            selected_project_id = st.selectbox(
                "Chọn dự án",
                options=[p['project_id'] for p in all_projects],
                format_func=lambda x: next((p['project_name'] for p in all_projects if p['project_id'] == x), x),
                key="project_selector"
            )
            
            if selected_project_id:
                proj_meta = pm.get_project_metadata(selected_project_id)
                if proj_meta:
                    st.info(f"**Query:** {proj_meta['user_query'][:50]}...")
                    st.caption(f"Searches: {proj_meta['search_count']} | Articles: {proj_meta['total_articles']}")
                    
                    # Action buttons
                    col_act1, col_act2 = st.columns(2)
                    
                    with col_act1:
                        # View project details
                        if st.button("📊 Xem chi tiết", key="view_project", use_container_width=True):
                            st.session_state.view_project_id = selected_project_id
                            st.rerun()
                    
                    with col_act2:
                        # Delete project
                        if st.button("🗑️ Xóa", key="delete_project", use_container_width=True):
                            if st.session_state.get('confirm_delete') == selected_project_id:
                                try:
                                    pm.delete_project(selected_project_id)
                                    st.success("✅ Đã xóa dự án")
                                    st.session_state.confirm_delete = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {e}")
                            else:
                                st.session_state.confirm_delete = selected_project_id
                                st.warning("⚠️ Nhấn lại để xác nhận xóa")
        else:
            st.info("Chưa có dự án nào. Tạo dự án mới sau khi tìm kiếm.")
        
        # Create new project option
        st.markdown("---")
        with st.expander("➕ Tạo dự án mới"):
            new_proj_name = st.text_input("Tên dự án", key="new_proj_name")
            new_proj_desc = st.text_area("Mô tả", key="new_proj_desc", height=80)
            new_proj_query = st.text_input("Query chính", key="new_proj_query")
            
            if st.button("Tạo dự án", key="create_proj"):
                if new_proj_name and new_proj_query:
                    try:
                        proj_id = pm.create_project(new_proj_name, new_proj_query, new_proj_desc)
                        st.success(f"✅ Đã tạo dự án: {proj_id}")
                        st.session_state.current_project_id = proj_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
                else:
                    st.warning("Vui lòng nhập tên và query")
    
    with tab_settings:
        st.header("⚙️ Cấu hình LangGraph")
        
        st.markdown("""
        ### 🧠 AI Orchestration
        - ✅ Tự động phân tích query
        - ✅ Tự động chọn nguồn tối ưu
        - ✅ Tự động refine nếu cần
        - ✅ Loại trùng lặp thông minh
        - ✅ Cache kết quả
        """)
        
        st.header("🔍 Bộ lọc")
        
        current_year = datetime.now().year
        year_range = st.slider(
            "Năm xuất bản",
            min_value=2000,
            max_value=current_year,
            value=(current_year-5, current_year)
        )
        
        max_results = st.number_input(
            "Số lượng kết quả tối đa", 
            min_value=5, 
            max_value=200, 
            value=50,
            help="AI sẽ tự động phân bổ cho các nguồn"
        )
        
        st.markdown("---")
        st.markdown("### Nguồn dữ liệu")
        st.info("💡 AI sẽ tự động chọn nguồn phù hợp, nhưng bạn có thể ưu tiên:")
        
        use_pubmed = st.checkbox("PubMed", value=True)
        use_scopus = st.checkbox("Scopus", value=False, help="Cần Scopus API key")
        use_semantic = st.checkbox("Semantic Scholar", value=True)
        
        st.markdown("---")
        st.markdown("### Thông tin hiển thị")
        show_authors = st.checkbox("Tác giả", value=True)
        show_journal = st.checkbox("Tạp chí", value=True)
        show_year = st.checkbox("Năm xuất bản", value=True)
        show_doi = st.checkbox("DOI", value=True)
        show_abstract = st.checkbox("Tóm tắt", value=True)
        show_citations = st.checkbox("Số lượt trích dẫn", value=True)
        
        st.markdown("---")
        st.markdown("### 🔧 Cơ chế tối ưu")
        st.markdown("""
        - 🗑️ **Deduplication**: DOI, PMID, Title similarity
        - 💾 **Cache**: 30 phút TTL
        - ⏱️ **Timeout**: 60s per source
        - 🔄 **Max Refinement**: 2 lần
        - 🎯 **Quality Threshold**: 0.7
        """)

# --- MAIN CONTENT ---
st.write("🧠 Trợ lý Tìm kiếm Y văn - LangGraph AI")

# Session State
if 'langgraph_results' not in st.session_state:
    st.session_state.langgraph_results = None
if 'graph_compiled' not in st.session_state:
    st.session_state.graph_compiled = None
if 'selected_articles' not in st.session_state:
    st.session_state.selected_articles = set()
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None
if 'view_project_id' not in st.session_state:
    st.session_state.view_project_id = None
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = None

# Compile graph once
if st.session_state.graph_compiled is None and gemini_key:
    with st.spinner("🔧 Compiling LangGraph workflow..."):
        try:
            st.session_state.graph_compiled = build_search_graph(
                gemini_api_key=gemini_key,
                pubmed_key=pubmed_key,
                scopus_key=scopus_key,
                semantic_key=semantic_key
            )
            st.success("✅ LangGraph workflow ready!")
        except Exception as e:
            st.error(f"❌ Failed to compile graph: {e}")

# Project Details View
if st.session_state.view_project_id:
    st.header(f"📊 Chi tiết Dự án")
    
    pm = ProjectManager()
    project_id = st.session_state.view_project_id
    
    # Get project metadata
    metadata = pm.get_project_metadata(project_id)
    
    if metadata:
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            st.metric("📚 Tổng bài báo", metadata['total_articles'])
        with col_p2:
            st.metric("🔍 Số lần tìm kiếm", metadata['search_count'])
        with col_p3:
            created = datetime.fromisoformat(metadata['created_at'])
            st.metric("📅 Ngày tạo", created.strftime("%d/%m/%Y"))
        
        st.markdown(f"**Query chính:** {metadata['user_query']}")
        if metadata.get('description'):
            st.markdown(f"**Mô tả:** {metadata['description']}")
        
        # Get all searches
        st.markdown("---")
        st.subheader("🔍 Lịch sử Tìm kiếm")
        
        searches = pm.get_project_searches(project_id)
        
        if searches:
            for search in searches:
                with st.expander(f"📝 {search['search_id']} - {search['saved_count']} bài báo (Quality: {search['quality_score']:.2f})"):
                    st.markdown(f"**Query:** {search['query']}")
                    st.caption(f"**Thời gian:** {search['timestamp']}")
                    
                    # Load full results button
                    if st.button(f"📖 Xem chi tiết", key=f"load_{search['search_id']}"):
                        search_data = pm.load_search_results(project_id, search['search_id'])
                        if search_data:
                            st.json(search_data)
        else:
            st.info("Chưa có tìm kiếm nào trong dự án này.")
        
        # Project history
        st.markdown("---")
        st.subheader("📜 Lịch sử Hoạt động")
        
        history = pm.get_project_history(project_id)
        
        if history:
            for entry in reversed(history[-10:]):  # Show last 10 entries
                timestamp = datetime.fromisoformat(entry['timestamp'])
                st.caption(f"**{timestamp.strftime('%d/%m/%Y %H:%M')}** - {entry['action']}")
                if entry.get('details'):
                    st.json(entry['details'])
        
        # Export section
        st.markdown("---")
        st.subheader("📥 Export")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📄 Export Summary (Markdown)", use_container_width=True):
                summary_md = pm.export_project_summary(project_id)
                st.download_button(
                    label="⬇️ Tải về Summary.md",
                    data=summary_md,
                    file_name=f"{metadata['project_name']}_summary.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        with col_exp2:
            if st.button("📊 Export Full Data (JSON)", use_container_width=True):
                # Combine all project data
                export_data = {
                    "metadata": metadata,
                    "searches": searches,
                    "history": history
                }
                st.download_button(
                    label="⬇️ Tải về Data.json",
                    data=json.dumps(export_data, indent=2, ensure_ascii=False),
                    file_name=f"{metadata['project_name']}_data.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Back button
        if st.button("⬅️ Quay lại"):
            st.session_state.view_project_id = None
            st.rerun()
        
        st.markdown("---")
        st.stop()  # Don't show the rest of the page

# === LAYOUT 2 CỘT CHÍNH ===
main_col1, main_col2 = st.columns([1, 1])

# ========== CỘT 1: GIỚI THIỆU + TÌM KIẾM ==========
with main_col1:
    st.markdown("""
    ### Hệ thống tìm kiếm thông minh với **AI orchestration**:
    
    - 🤖 **Tự động phân tích & tối ưu query**
    - 🚀 **Tìm kiếm song song (async)**
    - 🧹 **Loại trùng lặp thông minh (DOI, PMID, Title)**
    - 🔄 **Tự động refine nếu kết quả không tốt**
    - 💾 **Cache kết quả để tiết kiệm tài nguyên**
    """)
    
    # Search Input
    query = st.text_area(
        "Nội dung cần tìm kiếm", 
        height=150, 
        placeholder="Ví dụ: hãy tìm bài báo tiếng Anh cho chủ đề dùng trí thông minh nhân tạo trong chẩn đoán vết thương"
    )
    
    # Search Button
    if st.button("🚀 Tìm kiếm Thông minh (LangGraph AI)", type="primary", use_container_width=True):
        if not query:
            st.warning("⚠️ Vui lòng nhập nội dung cần tìm kiếm.")
        elif not gemini_key:
            st.error("❌ Vui lòng nhập GEMINI_API_KEY trong file .env")
        elif st.session_state.graph_compiled is None:
            st.error("❌ LangGraph workflow chưa sẵn sàng")
        else:
            # Prepare preferences
            sources = []
            if use_pubmed: sources.append("PubMed")
            if use_scopus: sources.append("Scopus")
            if use_semantic: sources.append("Semantic Scholar")
            
            if not sources:
                st.error("❌ Vui lòng chọn ít nhất một nguồn dữ liệu.")
            else:
                user_preferences = {
                    'max_results': max_results,
                    'year_range': list(year_range),
                    'sources': sources
                }
                
                # Execute LangGraph
                with st.spinner("🧠 AI đang phân tích và tìm kiếm..."):
                    try:
                        final_state = invoke_search(
                            st.session_state.graph_compiled,
                            user_query=query,
                            user_preferences=user_preferences
                        )
                        st.session_state.langgraph_results = final_state
                    except Exception as e:
                        st.error(f"❌ Search failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())

# ========== CỘT 2: KẾT QUẢ TÌM KIẾM ==========
with main_col2:
    # Display Results
    if st.session_state.langgraph_results:
        final_state = st.session_state.langgraph_results
        
        st.header("📊 Kết quả Tìm kiếm")
        
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
        
        st.markdown("---")
        
        # === PHẦN 2: LƯU KẾT QUẢ ===
        st.subheader("💾 Lưu Kết quả")
        
        # Selection controls
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            if st.button("☑️ Chọn tất cả", use_container_width=True, key="select_all_btn"):
                st.session_state.selected_articles = set(range(len(final_state['final_results'])))
                st.rerun()
        with col_sel2:
            if st.button("⬜ Bỏ chọn tất cả", use_container_width=True, key="deselect_all_btn"):
                st.session_state.selected_articles = set()
                st.rerun()
        
        # Project manager
        pm = ProjectManager()
        all_projects = pm.get_all_projects()
        
        # Project selection
        if all_projects:
            project_options = ["➕ Tạo dự án mới"] + [f"{p['project_name']} ({p['project_id']})" for p in all_projects]
            selected_proj = st.selectbox(
                "Chọn dự án",
                options=project_options,
                key="save_project_select"
            )
        else:
            selected_proj = "➕ Tạo dự án mới"
        
        # New project name input
        if selected_proj == "➕ Tạo dự án mới":
            new_project_name = st.text_input("Tên dự án mới", key="quick_new_proj")
        
        # Save mode selection
        col_mode1, col_mode2 = st.columns([2, 1])
        with col_mode1:
            save_mode = st.radio(
                "Chế độ lưu", 
                ["Tất cả", "Đã chọn"], 
                key="save_mode",
                horizontal=True
            )
        with col_mode2:
            if save_mode == "Đã chọn":
                st.metric("Đã chọn", len(st.session_state.selected_articles), delta=None)
        
        # Save button
        if st.button("💾 Lưu kết quả", type="primary", use_container_width=True, key="save_results_btn"):
            try:
                # Determine project ID
                if selected_proj == "➕ Tạo dự án mới":
                    if not new_project_name:
                        st.error("❌ Vui lòng nhập tên dự án mới")
                    else:
                        # Create new project
                        project_id = pm.create_project(
                            project_name=new_project_name,
                            user_query=final_state.get('user_query', ''),
                            description=f"Auto-created from search"
                        )
                        st.session_state.current_project_id = project_id
                else:
                    # Extract project ID from selection
                    project_id = selected_proj.split('(')[-1].strip(')')
                
                # Determine articles to save
                if save_mode == "Tất cả":
                    articles_to_save = final_state['final_results']
                else:
                    # Get selected articles
                    articles_to_save = [
                        art for i, art in enumerate(final_state['final_results'])
                        if i in st.session_state.selected_articles
                    ]
                
                if not articles_to_save:
                    st.warning("⚠️ Không có bài báo nào để lưu")
                else:
                    # Save results
                    search_id = pm.save_search_results(
                        project_id=project_id,
                        search_results=final_state,
                        selected_articles=articles_to_save
                    )
                    
                    st.success(f"✅ Đã lưu {len(articles_to_save)} bài báo vào dự án")
                    st.info(f"📋 Search ID: {search_id}")
                    
                    # Reset selection
                    st.session_state.selected_articles = set()
                    
            except Exception as e:
                st.error(f"❌ Lỗi khi lưu: {e}")
                import traceback
                st.code(traceback.format_exc())
        
        st.markdown("---")
        
        # === PHẦN 3: CHIẾN LƯỢC AI ===
        with st.expander("🧠 Chiến lược AI đã sử dụng", expanded=False):
            tab_analysis, tab_strategy = st.tabs(["📊 Phân tích Query", "📋 Chiến lược Tìm kiếm"])
            
            with tab_analysis:
                if final_state.get('query_analysis'):
                    analysis = final_state['query_analysis']
                    st.json(analysis)
                else:
                    st.info("Không có dữ liệu phân tích")
            
            with tab_strategy:
                if final_state.get('search_strategy'):
                    strategy = final_state['search_strategy']
                    st.json(strategy)
                else:
                    st.info("Không có dữ liệu chiến lược")
        
        # === PHẦN 4: WORKFLOW LOG ===
        with st.expander("📜 Workflow Log", expanded=False):
            messages = final_state.get('messages', [])
            if messages:
                for msg in messages:
                    # Handle both dict and SystemMessage objects
                    if isinstance(msg, dict):
                        st.text(msg.get('content', ''))
                    elif hasattr(msg, 'content'):
                        st.text(msg.content)
                    else:
                        st.text(str(msg))
            else:
                st.info("Không có log workflow")
    else:
        # Empty state
        st.markdown("### 📊 Kết quả Tìm kiếm")
        st.info("👈 Nhập nội dung tìm kiếm và nhấn nút **'Tìm kiếm Thông minh'** để bắt đầu")
        
        # Placeholder metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Bài báo", "0")
        with col2:
            st.metric("⭐ Chất lượng", "0.00")
        with col3:
            st.metric("🔄 Refinement", "0/2")
        with col4:
            st.metric("🗑️ Đã loại", "0")

# === PHẦN HIỂN THỊ BÀI BÁO (FULL WIDTH) ===
if st.session_state.langgraph_results:
    final_state = st.session_state.langgraph_results
    
    st.markdown("---")
    
    # Articles
    articles = final_state['final_results']
    
    if not articles:
        st.warning("⚠️ Không tìm thấy bài báo nào.")
    else:
        # Filter by source
        pubmed_articles = [a for a in articles if a['source'] == 'PubMed']
        scopus_articles = [a for a in articles if a['source'] == 'Scopus']
        semantic_articles = [a for a in articles if a['source'] == 'Semantic Scholar']
        
        tab1, tab2, tab3, tab4 = st.tabs([
            f"🌍 Tất cả ({len(articles)})", 
            f"🔬 PubMed ({len(pubmed_articles)})", 
            f"📚 Scopus ({len(scopus_articles)})", 
            f"🌐 Semantic Scholar ({len(semantic_articles)})"
        ])
        
        def display_article(article, idx, tab_prefix=""):
            with st.container():
                # Checkbox để chọn bài báo
                col_check, col_content = st.columns([0.5, 11.5])
                
                with col_check:
                    # Use actual index in final_results for tracking
                    article_index = idx - 1  # Convert from 1-based to 0-based
                    is_selected = article_index in st.session_state.selected_articles
                    
                    if st.checkbox("", value=is_selected, key=f"select_{tab_prefix}_{idx}_{article.get('doi', article.get('title', '')[:20])}"):
                        st.session_state.selected_articles.add(article_index)
                    else:
                        st.session_state.selected_articles.discard(article_index)
                
                with col_content:
                    # Title with link
                    link = article.get('link', '#')
                    title = article.get('title', 'N/A')
                    st.markdown(f"### {idx}. [{title}]({link})")
                    
                    # Caption
                    caption_parts = [f"**Nguồn:** {article['source']}"]
                    if show_year:
                        caption_parts.append(f"**Năm:** {article['year']}")
                    if show_journal:
                        caption_parts.append(f"**Tạp chí:** {article['journal']}")
                    if show_citations and article.get('cited_by', 'N/A') != 'N/A':
                        caption_parts.append(f"**📊 Trích dẫn:** {article['cited_by']}")
                    
                    st.caption(" | ".join(caption_parts))
                    
                    # Authors
                    if show_authors and article.get('authors'):
                        authors = article['authors']
                        authors_display = ', '.join(authors[:3])
                        if len(authors) > 3:
                            authors_display += f" et al. (+{len(authors)-3})"
                        st.markdown(f"**👥 Tác giả:** {authors_display}")
                    
                    # DOI & IDs
                    if show_doi:
                        doi = article.get('doi', 'N/A')
                        if doi != 'N/A':
                            st.markdown(f"**🔗 DOI:** `{doi}`")
                        
                        pmid = article.get('pmid', 'N/A')
                        if pmid != 'N/A':
                            st.markdown(f"**🔬 PMID:** `{pmid}`")
                        
                        pmc_id = article.get('pmc_id', 'N/A')
                        if pmc_id != 'N/A':
                            st.markdown(f"**📄 PMC ID:** `{pmc_id}`")
                    
                    # Abstract
                    if show_abstract and article.get('abstract', 'N/A') != 'N/A':
                        with st.expander("📄 Xem tóm tắt"):
                            st.markdown(article['abstract'])
                
                st.markdown("---")
        
        with tab1:
            for i, article in enumerate(articles, 1):
                display_article(article, i, "all")
        
        with tab2:
            if not pubmed_articles:
                st.info("ℹ️ Không có kết quả từ PubMed.")
            else:
                for i, article in enumerate(pubmed_articles, 1):
                    display_article(article, i, "pubmed")
        
        with tab3:
            if not scopus_articles:
                st.info("ℹ️ Không có kết quả từ Scopus.")
            else:
                for i, article in enumerate(scopus_articles, 1):
                    display_article(article, i, "scopus")
        
        with tab4:
            if not semantic_articles:
                st.info("ℹ️ Không có kết quả từ Semantic Scholar.")
            else:
                for i, article in enumerate(semantic_articles, 1):
                    display_article(article, i, "semantic")

# Footer
st.markdown("---")
st.markdown("""
### 🚀 Tính năng LangGraph AI
- **Tự động phân tích**: AI nhận diện topic, language, complexity
- **Tự động tối ưu**: Tạo query riêng cho PubMed (MeSH), Scopus, Semantic Scholar
- **Tìm kiếm song song**: Async parallel search để tiết kiệm thời gian
- **Deduplication**: Loại trùng lặp theo DOI → PMID → Title similarity (85%)
- **Cache thông minh**: Lưu kết quả 30 phút, tránh gọi API lại
- **Auto refinement**: Tự động cải thiện query nếu kết quả không đạt (max 2 lần)
- **Early stopping**: Dừng khi quality_score >= 0.7 hoặc đủ 80% kết quả

### 🛑 Điều kiện dừng tìm kiếm:
1. ✅ **Quality score >= 0.7** (kết quả tốt)
2. ✅ **Tìm được >= 80%** số lượng mong muốn
3. ✅ **Đã refine 2 lần** (tránh vòng lặp vô hạn)
""")
