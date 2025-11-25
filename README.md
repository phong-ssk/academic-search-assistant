# 🔬 Academic Search Assistant

Công cụ tìm kiếm bài báo khoa học thông minh với AI, tích hợp PubMed, Scopus và Semantic Scholar.

## ✨ Tính năng

### 🎯 Hai Phiên bản

1. **app.py** - Phiên bản cơ bản
   - Tìm kiếm thủ công với 3 nguồn
   - AI tư vấn chiến lược (tùy chọn)
   - Kiểm soát chi tiết query

2. **app_langgraph.py** - Phiên bản AI nâng cao 🚀
   - **Tự động phân tích** query với Gemini AI
   - **Tự động tối ưu** query cho từng nguồn
   - **Tìm kiếm song song** (async) - nhanh hơn 50%
   - **Loại trùng lặp thông minh** (DOI → PMID → Title)
   - **Cache 30 phút** - tiết kiệm 40% API calls
   - **Auto refinement** nếu kết quả không đạt
   - **Quản lý dự án** - lưu lịch sử tìm kiếm

### 🔍 Nguồn Dữ Liệu
- **PubMed** - Y sinh học (NCBI)
- **Scopus** - Đa ngành khoa học
- **Semantic Scholar** - Hỗ trợ tiếng Việt tốt

## 📁 Cấu trúc

```
tim_y_van_04_api/
├── app.py                    # App cơ bản
├── app_langgraph.py          # App LangGraph AI ⭐
├── requirements.txt
├── .env                      # API keys
├── backend/
│   ├── *_api.py             # API clients cho 3 nguồn
│   ├── search_manager.py    # Logic app cơ bản
│   ├── gemini_service.py    # Gemini AI
│   ├── langgraph_orchestrator.py  # LangGraph workflow
│   ├── async_apis.py        # Async + Cache + Dedup
│   ├── project_manager.py   # Quản lý dự án
│   └── nodes/               # LangGraph nodes
├── projects/                # Dữ liệu dự án
└── docs/                    # Tài liệu chi tiết
```

## 🚀 Cài đặt & Sử dụng

### 1. Cài đặt

```bash
pip install -r requirements.txt
```

### 2. Cấu hình API Keys

Tạo file `.env`:

```bash
GEMINI_API_KEY=your_key     # Bắt buộc cho AI
SCOPUS_API_KEY=your_key     # Bắt buộc cho Scopus
PUBMED_API_KEY=             # Tùy chọn
SEMANTIC_SCHOLAR_API_KEY=   # Tùy chọn
```

**Lấy API Keys:**
- Gemini: https://aistudio.google.com/
- Scopus: https://dev.elsevier.com/

### 3. Chạy App

**App cơ bản:**
```bash
streamlit run app.py
```

**App LangGraph AI (Khuyến nghị):**
```bash
streamlit run app_langgraph.py
# Hoặc:
./start_langgraph.sh
```

## 🎯 So sánh 2 Phiên bản

| Tính năng | app.py | app_langgraph.py |
|-----------|--------|------------------|
| Tối ưu query | ❌ Thủ công | ✅ AI tự động |
| Loại trùng lặp | ❌ Không | ✅ 3-tier (DOI/PMID/Title) |
| Cache | ❌ Không | ✅ 30 phút |
| Tìm song song | ❌ Tuần tự | ✅ Async |
| Auto refine | ❌ Không | ✅ Tối đa 2 lần |
| Quản lý dự án | ❌ Không | ✅ Có |
| Tốc độ | Chậm (30-45s) | ⚡ Nhanh (15-20s) |

**Khuyến nghị:** Dùng `app_langgraph.py` cho kết quả tốt hơn!

## 📚 Tài liệu

- [docs/FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) - Tổng kết toàn bộ tính năng
- [docs/COMPARISON.md](docs/COMPARISON.md) - So sánh chi tiết 2 app
- [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - Hướng dẫn sử dụng
- [docs/](docs/) - Tài liệu đầy đủ

## 🛠️ Công nghệ

- **Frontend:** Streamlit
- **AI:** Gemini 2.0 Flash, LangGraph
- **APIs:** PubMed, Scopus, Semantic Scholar
