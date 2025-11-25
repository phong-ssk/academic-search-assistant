# 📖 Hướng Dẫn Sử Dụng Chi Tiết

## 🎯 Kịch Bản 1: Tìm Kiếm Với AI (Khuyên Dùng)

### Bước 1: Nhập Query
Nhập chủ đề cần tìm bằng tiếng Việt hoặc tiếng Anh:
```
Ví dụ: "Điều trị tăng huyết áp ở người cao tuổi bằng thuốc ức chế men chuyển"
```

### Bước 2: Tư Vấn AI
1. Bấm nút **"🤖 Tư vấn Chiến lược Tìm kiếm (AI)"**
2. Đợi AI phân tích (5-10 giây)
3. Xem kết quả tư vấn:
   - **Chiến lược tìm kiếm:** PICO, từ khóa MeSH, toán tử Boolean
   - **Query tiếng Anh:** Đã tối ưu cho PubMed/Scopus
   - **Query tiếng Việt:** Đã tối ưu cho Semantic Scholar

### Bước 3: Chọn Nguồn Tìm Kiếm
Trong sidebar, chọn các nguồn muốn tìm:
- ☑️ PubMed (miễn phí, y sinh học)
- ☐ Scopus (cần API key, đa ngành)
- ☑️ Semantic Scholar (miễn phí, đa ngành, hỗ trợ VN)

### Bước 4: Tìm Kiếm
Bấm **"🔍 Tìm kiếm với Query AI"**
- PubMed/Scopus sẽ dùng query tiếng Anh đã tối ưu
- Semantic Scholar sẽ dùng query tiếng Việt đã tối ưu

### Bước 5: Xem Kết Quả
- Kết quả hiển thị với badge ✨ "AI-optimized"
- Có thể mở rộng để xem query đã sử dụng
- Mỗi bài báo hiển thị:
  - Tiêu đề (link đến nguồn)
  - Tác giả (tối đa 3 + et al.)
  - Tạp chí, năm, số trích dẫn
  - DOI (nếu có)
  - Tóm tắt (ẩn trong expander)

---

## 🔧 Kịch Bản 2: Tìm Kiếm Trực Tiếp (Không Dùng AI)

### Khi Nào Dùng:
- Bạn đã có query tối ưu sẵn
- Không có Gemini API key
- Muốn kiểm soát 100% query

### Các Bước:
1. Nhập query vào ô tìm kiếm
2. Chọn nguồn trong sidebar
3. Bấm **"🔍 Tìm kiếm với Query gốc"**
4. Kết quả hiển thị với badge 📝 "Original"

---

## ⚙️ Tùy Chỉnh Hiển Thị

Trong sidebar → **"Thông tin hiển thị"**, bỏ chọn các trường không cần:

- **Tác giả:** Danh sách tác giả (tối đa 3)
- **Tạp chí:** Tên tạp chí/hội nghị
- **Năm xuất bản:** Năm công bố
- **DOI:** Digital Object Identifier
- **Tóm tắt:** Abstract đầy đủ
- **Số lượt trích dẫn:** Citation count (Scopus/Semantic Scholar)

Ví dụ: Chỉ muốn xem tiêu đề + DOI → Bỏ chọn các ô khác.

---

## 🔑 Cấu Hình API Keys

### File .env
Mở file `.env` và điền API keys:

```bash
# Bắt buộc cho tính năng AI
GEMINI_API_KEY=AIzaSy...

# Không bắt buộc nhưng tăng rate limit
PUBMED_API_KEY=

# Bắt buộc để dùng Scopus
SCOPUS_API_KEY=

# Không bắt buộc
SEMANTIC_SCHOLAR_API_KEY=
```

### Lấy API Keys:

**Gemini:**
1. Vào https://aistudio.google.com/
2. Đăng nhập Google account
3. Click "Get API Key" → "Create API key"
4. Copy và paste vào .env

**Scopus:**
1. Vào https://dev.elsevier.com/
2. Đăng ký account
3. Tạo application mới
4. Copy API key

**PubMed:**
1. Vào https://www.ncbi.nlm.nih.gov/account/
2. Đăng ký NCBI account
3. Settings → API Key

**Semantic Scholar:**
1. Vào https://www.semanticscholar.org/product/api
2. Request API key (không bắt buộc)

---

## 🎓 Tips & Best Practices

### 1. Tối Ưu Query Tiếng Việt
Nếu nhập tiếng Việt, AI sẽ:
- Dịch sang tiếng Anh với thuật ngữ y khoa chính xác
- Thêm MeSH terms cho PubMed
- Giữ nguyên tiếng Việt cho Semantic Scholar

### 2. Sử Dụng PICO
AI tư vấn sẽ gợi ý cấu trúc PICO:
- **P**opulation: Người cao tuổi, trẻ em, thai phụ...
- **I**ntervention: Thuốc, phẫu thuật, liệu pháp...
- **C**omparison: So sánh với gì?
- **O**utcome: Kết quả mong đợi

### 3. Bộ Lọc Năm
Trong sidebar, điều chỉnh slider để chọn khoảng năm:
- Nghiên cứu mới nhất: 2023-2025
- Review systematic: 2015-2025
- Tài liệu lịch sử: 2000-2010

### 4. Số Lượng Kết Quả
- **5 kết quả:** Quick scan
- **10-20 kết quả:** Tìm hiểu sâu
- **30-50 kết quả:** Systematic review

### 5. So Sánh Nguồn
Tìm cùng lúc trên cả 3 nguồn để:
- So sánh độ phủ
- Tránh bỏ sót
- Cross-reference

---

## 🐛 Xử Lý Lỗi

### Lỗi: "Gemini API Key invalid"
- Kiểm tra key trong .env
- Đảm bảo không có khoảng trắng
- Key phải bắt đầu bằng `AIzaSy...`

### Lỗi: "Scopus authentication failed"
- Kiểm tra Scopus API key
- Đảm bảo account còn quota
- Scopus yêu cầu institutional access cho một số tính năng

### Lỗi: "Rate limit exceeded"
- Đợi 1-2 phút
- Hoặc nhập API key để tăng limit
- PubMed: 10 req/s (có key) vs 3 req/s (không key)
- Semantic Scholar: 100 req/5min (có key) vs 1 req/s (không key)

### Không Có Kết Quả
- Thử query đơn giản hơn
- Bỏ bộ lọc năm
- Dùng AI để tối ưu query
- Kiểm tra chính tả

---

## 📊 Hiểu Kết Quả

### Citation Count
- **Cao (>100):** Highly cited, influential
- **Trung bình (10-100):** Well-established
- **Thấp (<10):** Mới hoặc niche topic

### DOI
- Click vào để xem full text (nếu có access)
- Dùng Sci-Hub nếu không có subscription (tự chịu trách nhiệm)

### PMC ID
- Bài báo có PMC = Open Access
- Có thể đọc full text miễn phí tại https://www.ncbi.nlm.nih.gov/pmc/

---

## 🚀 Workflow Khuyên Dùng

```
1. Nhập query tiếng Việt
   ↓
2. Tư vấn AI → Xem strategy
   ↓
3. Tìm với Query AI (3 nguồn)
   ↓
4. Xem tab "Tất cả" → Quick overview
   ↓
5. Xem từng tab nguồn → So sánh
   ↓
6. Click DOI → Đọc full text
   ↓
7. (Optional) Export kết quả
```

---

*Có câu hỏi? Mở issue tại: https://github.com/phong-ssk/academic-search-assistant/issues*
