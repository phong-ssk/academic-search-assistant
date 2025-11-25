import streamlit as st
from backend.search_manager import SearchManager
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cấu hình trang
st.set_page_config(
    page_title="Academic Search Assistant",
    page_icon="🎓",
    layout="wide"
)

# Load API keys from .env
gemini_key = os.getenv("GEMINI_API_KEY", "")
pubmed_key = os.getenv("PUBMED_API_KEY", "")
scopus_key = os.getenv("SCOPUS_API_KEY", "")
semantic_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cấu hình")

    st.header("🔍 Bộ lọc")
    
    current_year = datetime.now().year
    year_range = st.slider(
        "Năm xuất bản",
        min_value=2000,
        max_value=current_year,
        value=(current_year-5, current_year)
    )
    
    max_results = st.number_input("Số lượng kết quả tối đa", min_value=1, max_value=100, value=10)
    
    st.markdown("---")
    st.markdown("### Nguồn dữ liệu")
    use_pubmed = st.checkbox("PubMed", value=True)
    use_scopus = st.checkbox("Scopus", value=False)
    use_semantic = st.checkbox("Semantic Scholar", value=True)
    
    st.markdown("---")
    st.markdown("### Thông tin hiển thị")
    show_authors = st.checkbox("Tác giả", value=True)
    show_journal = st.checkbox("Tạp chí", value=True)
    show_year = st.checkbox("Năm xuất bản", value=True)
    show_doi = st.checkbox("DOI", value=True)
    show_abstract = st.checkbox("Tóm tắt", value=True)
    show_citations = st.checkbox("Số lượt trích dẫn", value=True)

# --- MAIN CONTENT ---
st.title("🎓 Trợ lý Tìm kiếm Y văn Thông minh")
st.markdown("Hệ thống tìm kiếm tích hợp AI, hỗ trợ PubMed, Scopus và Semantic Scholar.")

# Initialize Manager
manager = SearchManager(
    pubmed_key=pubmed_key,
    scopus_key=scopus_key,
    gemini_key=gemini_key,
    semantic_key=semantic_key
)

# Session State
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'consultation' not in st.session_state:
    st.session_state.consultation = ""
if 'optimized_en_query' not in st.session_state:
    st.session_state.optimized_en_query = ""
if 'optimized_vn_query' not in st.session_state:
    st.session_state.optimized_vn_query = ""
if 'strategy' not in st.session_state:
    st.session_state.strategy = ""

# Search Input
query = st.text_area("Nội dung cần tìm kiếm", height=100, placeholder="Ví dụ: Điều trị tăng huyết áp ở người cao tuổi...")

# AI Consultation Button
if st.button("🤖 Tư vấn Chiến lược Tìm kiếm (AI)", use_container_width=True):
    if not query:
        st.warning("Vui lòng nhập nội dung cần tìm kiếm.")
    elif not gemini_key:
        st.error("Vui lòng nhập Gemini API Key trong file .env để sử dụng tính năng này.")
    else:
        with st.spinner("AI đang phân tích và tối ưu hóa..."):
            # Get consultation
            consultation = manager.consult(query)
            st.session_state.consultation = consultation
            
            # Get optimized queries
            optimization = manager.gemini.optimize_query(query)
            st.session_state.optimized_en_query = optimization.get("english_query", query)
            st.session_state.optimized_vn_query = optimization.get("vietnamese_query", query)
            st.session_state.strategy = optimization.get("strategy", "")

# Display Consultation and Optimized Queries
if st.session_state.consultation:
    with st.expander("💡 Tư vấn từ AI", expanded=True):
        st.markdown(st.session_state.consultation)
        
        if st.session_state.optimized_en_query or st.session_state.optimized_vn_query:
            st.markdown("---")
            st.markdown("### 🎯 Query đã tối ưu hóa")
            
            if st.session_state.optimized_en_query:
                st.info(f"**🇬🇧 Tiếng Anh (PubMed/Scopus):**\n\n`{st.session_state.optimized_en_query}`")
            
            if st.session_state.optimized_vn_query:
                st.success(f"**🇻🇳 Tiếng Việt (Semantic Scholar):**\n\n`{st.session_state.optimized_vn_query}`")
            
            if st.session_state.strategy:
                st.markdown(f"**📋 Chiến lược:** {st.session_state.strategy}")

# Search Buttons
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    use_ai_query = st.button("🔍 Tìm kiếm với Query AI", type="primary", use_container_width=True, 
                             disabled=not st.session_state.optimized_en_query)
    
with col2:
    use_original_query = st.button("🔍 Tìm kiếm với Query gốc", use_container_width=True)

# Execute Search
if use_ai_query or use_original_query:
    if not query:
        st.warning("Vui lòng nhập nội dung cần tìm kiếm.")
    else:
        sources = []
        if use_pubmed: sources.append("PubMed")
        if use_scopus: sources.append("Scopus")
        if use_semantic: sources.append("Semantic Scholar")
        
        if not sources:
            st.error("Vui lòng chọn ít nhất một nguồn dữ liệu.")
        else:
            # Determine which queries to use
            if use_ai_query and st.session_state.optimized_en_query:
                english_query = st.session_state.optimized_en_query
                vietnamese_query = st.session_state.optimized_vn_query
                search_mode = "AI-optimized"
            else:
                english_query = query
                vietnamese_query = query
                search_mode = "Original"
            
            with st.spinner("Đang tìm kiếm..."):
                results = manager.process_search_with_custom_queries(
                    english_query=english_query,
                    vietnamese_query=vietnamese_query,
                    sources=sources,
                    max_results=max_results,
                    year_start=year_range[0],
                    year_end=year_range[1],
                    search_mode=search_mode
                )
                st.session_state.search_results = results

# Display Results
if st.session_state.search_results:
    results = st.session_state.search_results
    
    st.markdown("---")
    st.header("📚 Kết quả Tìm kiếm")
    
    # Display search mode info
    if results.get("search_mode"):
        mode = results["search_mode"]
        if mode == "AI-optimized":
            st.success("✨ **Đang hiển thị kết quả với Query AI đã tối ưu hóa**")
        else:
            st.info("📝 **Đang hiển thị kết quả với Query gốc của bạn**")
    
    # Display queries used
    if results.get("queries_used"):
        queries = results["queries_used"]
        with st.expander("🔎 Query đã sử dụng", expanded=False):
            if queries.get("english"):
                st.markdown(f"**🇬🇧 Tiếng Anh (PubMed/Scopus):** `{queries['english']}`")
            if queries.get("vietnamese"):
                st.markdown(f"**🇻🇳 Tiếng Việt (Semantic Scholar):** `{queries['vietnamese']}`")
    
    # Errors
    if results.get("errors"):
        for error in results["errors"]:
            st.error(error)
            
    # Articles
    articles = results.get("articles", [])
    if not articles:
        st.warning("Không tìm thấy bài báo nào.")
    else:
        # Filter by source for tabs
        pubmed_articles = [a for a in articles if a['source'] == 'PubMed']
        scopus_articles = [a for a in articles if a['source'] == 'Scopus']
        semantic_articles = [a for a in articles if a['source'] == 'Semantic Scholar']
        
        tab1, tab2, tab3, tab4 = st.tabs([
            f"Tất cả ({len(articles)})", 
            f"PubMed ({len(pubmed_articles)})", 
            f"Scopus ({len(scopus_articles)})", 
            f"Semantic Scholar ({len(semantic_articles)})"
        ])
        
        def display_article(article, idx):
            with st.container():
                st.markdown(f"### {idx}. [{article['title']}]({article.get('link', '#')})")
                
                # Build caption with selected fields
                caption_parts = [f"**Nguồn:** {article['source']}"]
                if show_year:
                    caption_parts.append(f"**Năm:** {article['year']}")
                if show_journal:
                    caption_parts.append(f"**Tạp chí:** {article['journal']}")
                if show_citations and article.get('cited_by', 'N/A') != 'N/A':
                    caption_parts.append(f"**Trích dẫn:** {article['cited_by']}")
                
                st.caption(" | ".join(caption_parts))
                
                if show_authors and article.get('authors'):
                    authors_display = ', '.join(article['authors'][:3])
                    if len(article['authors']) > 3:
                        authors_display += " et al."
                    st.markdown(f"**Tác giả:** {authors_display}")
                
                if show_doi and article.get('doi', 'N/A') != 'N/A':
                    st.markdown(f"**DOI:** {article['doi']}")
                
                if article.get('pmc_id', 'N/A') != 'N/A':
                    st.markdown(f"**PMC ID:** {article['pmc_id']}")
                
                if show_abstract and article.get('abstract', 'N/A') != 'N/A':
                    with st.expander("Xem tóm tắt"):
                        st.markdown(article['abstract'])
                
                st.markdown("---")

        with tab1:
            for i, article in enumerate(articles, 1):
                display_article(article, i)
                
        with tab2:
            for i, article in enumerate(pubmed_articles, 1):
                display_article(article, i)
                
        with tab3:
            if not use_scopus:
                st.info("Chưa chọn nguồn Scopus.")
            elif not scopus_articles:
                st.info("Không có kết quả từ Scopus.")
            else:
                for i, article in enumerate(scopus_articles, 1):
                    display_article(article, i)

        with tab4:
            if not use_semantic:
                st.info("Chưa chọn nguồn Semantic Scholar.")
            elif not semantic_articles:
                st.info("Không có kết quả từ Semantic Scholar.")
            else:
                for i, article in enumerate(semantic_articles, 1):
                    display_article(article, i)
