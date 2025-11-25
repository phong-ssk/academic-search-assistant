# 📚 Tài liệu

Thư mục chứa tài liệu chi tiết về Academic Search Assistant.

## 📄 Danh sách

### 1. [FINAL_SUMMARY.md](FINAL_SUMMARY.md) ⭐
Tổng kết đầy đủ về tính năng LangGraph:
- Trả lời 3 câu hỏi chính: Khi nào dừng? Loại trùng lặp? Tiết kiệm tài nguyên?
- Performance metrics và số liệu
- Files đã tạo và cấu trúc
- Tính năng chi tiết

### 2. [COMPARISON.md](COMPARISON.md)
So sánh chi tiết app.py vs app_langgraph.py:
- Query optimization
- Source selection
- Deduplication
- Caching & Performance
- Resource efficiency
- Đề xuất sử dụng cho từng scenario

### 3. [USAGE_GUIDE.md](USAGE_GUIDE.md)
Hướng dẫn sử dụng từng bước:
- Kịch bản tìm kiếm với AI
- Kịch bản tìm kiếm trực tiếp
- Tùy chỉnh hiển thị
- Cấu hình API keys
- Tips & Best practices
- Xử lý lỗi thường gặp

### 4. [LANGGRAPH_README.md](LANGGRAPH_README.md)
Tài liệu kỹ thuật LangGraph:
- Tổng quan kiến trúc
- 6 tính năng chính
- Workflow flow
- Configuration
- Cấu trúc files
- Use cases

---

## 🚀 Bắt đầu

Nếu bạn mới bắt đầu:
1. Đọc [README.md](../README.md) ở thư mục gốc
2. Chạy `streamlit run app_langgraph.py`
3. Quay lại đọc [USAGE_GUIDE.md](USAGE_GUIDE.md) để hiểu rõ hơn

Nếu bạn là developer:
1. Đọc [FINAL_SUMMARY.md](FINAL_SUMMARY.md) để hiểu kiến trúc
2. Đọc [LANGGRAPH_README.md](LANGGRAPH_README.md) để hiểu workflow
3. Xem code trong `backend/nodes/` và `backend/langgraph_orchestrator.py`
