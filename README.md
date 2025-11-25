# 🔬 Academic Search Assistant (Trợ lý Tìm kiếm Y văn)

Công cụ tìm kiếm bài báo khoa học thông minh, tích hợp đa nguồn (PubMed, Scopus, Semantic Scholar) và AI tư vấn chiến lược (Gemini).

## ✨ Tính năng Nổi bật

### 1. 🔍 Đa Nguồn Dữ Liệu
- **PubMed**: Tìm kiếm y văn y sinh học từ cơ sở dữ liệu NCBI (Tiếng Anh).
- **Scopus**: Tìm kiếm tài liệu khoa học đa ngành (Tiếng Anh).
- **Semantic Scholar**: Tìm kiếm thông minh với Semantic Graph (Hỗ trợ tốt cho cả Tiếng Việt & Anh).

### 2. 🤖 Trợ lý AI (Gemini)
- **Tư vấn Chiến lược**: Đóng vai trò thủ thư y khoa, gợi ý từ khóa (MeSH terms), cấu trúc PICO, và chiến lược tìm kiếm hiệu quả.
- **Tối ưu hóa Truy vấn**: Tự động chuyển đổi câu hỏi tự nhiên thành truy vấn tối ưu cho từng nguồn:
    - *Tiếng Anh* cho PubMed/Scopus.
    - *Tiếng Việt* cho Semantic Scholar.

### 3. � Giao diện Thân thiện
- **Sidebar Cấu hình**: Quản lý API Keys và bộ lọc tìm kiếm (Năm, Số lượng) dễ dàng.
- **Kết quả Phân loại**: Hiển thị kết quả theo từng tab nguồn riêng biệt hoặc tổng hợp.
- **Lưu trữ**: (Tùy chọn) Lưu kết quả tìm kiếm để tham khảo sau.

## 📁 Cấu trúc Dự án

```
tim_y_van_04_api/
├── app.py                       # Frontend (Streamlit UI)
├── requirements.txt             # Các thư viện cần thiết
├── README.md                    # Tài liệu hướng dẫn
│
├── backend/                     # Backend Logic
│   ├── __init__.py
│   ├── search_manager.py        # Quản lý & điều phối tìm kiếm
│   ├── gemini_service.py        # Tích hợp Google Gemini (google-genai SDK)
│   ├── pubmed_api.py            # API Client cho PubMed
│   ├── scopus_api.py            # API Client cho Scopus
│   └── semantic_scholar_api.py  # API Client cho Semantic Scholar
│
└── results/                     # Thư mục chứa kết quả (nếu có lưu)
```

## 🚀 Hướng dẫn Cài đặt & Sử dụng

### 1. Cài đặt Môi trường

Yêu cầu Python 3.9 trở lên.

```bash
# Clone dự án (nếu chưa có)
# git clone ...

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 2. Cấu hình API Keys

Tạo file `.env` từ file mẫu và điền các API keys:

```bash
cp .env.example .env
```

Sau đó chỉnh sửa file `.env` và điền các API keys của bạn:

```
GEMINI_API_KEY=your_gemini_api_key_here
PUBMED_API_KEY=your_pubmed_api_key_here
SCOPUS_API_KEY=your_scopus_api_key_here
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key_here
```

**Lấy API Keys:**
*   **Gemini API Key** (Bắt buộc cho tính năng AI): [Lấy tại Google AI Studio](https://aistudio.google.com/)
*   **Scopus API Key** (Bắt buộc cho Scopus): [Lấy tại Elsevier Developer](https://dev.elsevier.com/)
*   **PubMed / Semantic Scholar**: Không bắt buộc, nhưng nên nhập để tăng giới hạn tìm kiếm (Rate Limit)

### 3. Chạy Ứng dụng

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại `http://localhost:8501`.

## � Kịch bản Sử dụng Điển hình

1.  **Bước 1**: Nhập chủ đề cần tìm vào ô tìm kiếm (ví dụ: "Điều trị tiểu đường bằng thuốc nam").
2.  **Bước 2**: Bấm **"Tư vấn Chiến lược (AI)"** để xem AI gợi ý từ khóa và cách tìm.
3.  **Bước 3**: Chọn các nguồn muốn tìm (ví dụ: cả 3 nguồn).
4.  **Bước 4**: Bấm **"Tìm kiếm Ngay"**.
    *   Hệ thống sẽ tự động dịch và tối ưu từ khóa sang tiếng Anh để tìm trên PubMed/Scopus.
    *   Đồng thời tìm bằng tiếng Việt trên Semantic Scholar.
5.  **Bước 5**: Xem và so sánh kết quả tại các Tab.

## 🛠️ Công nghệ Sử dụng

- **Frontend**: Streamlit
- **AI Model**: Gemini 2.0 Flash (via `google-genai` SDK)
- **APIs**: NCBI Entrez (PubMed), Scopus Search API, Semantic Scholar Graph API
