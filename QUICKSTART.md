# ⚡ Chạy Nhanh

## 🚀 Cách chạy 2 app

### App LangGraph AI (Khuyến nghị) ⭐
```bash
./start_langgraph.sh
# Hoặc:
streamlit run app_langgraph.py
```

### App Cơ bản
```bash
streamlit run app.py
```

## ⚙️ Cài đặt lần đầu

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Tạo file .env
cat > .env << EOF
GEMINI_API_KEY=your_key
SCOPUS_API_KEY=your_key
PUBMED_API_KEY=
SEMANTIC_SCHOLAR_API_KEY=
EOF

# 3. Chạy
./start_langgraph.sh
```

## 📚 Tài liệu

- [README.md](README.md) - Hướng dẫn đầy đủ
- [docs/](docs/) - Tài liệu chi tiết
- [ORGANIZATION.md](ORGANIZATION.md) - Cấu trúc dự án
