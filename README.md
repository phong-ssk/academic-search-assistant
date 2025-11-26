# 🔬 Academic Search Assistant with AI Orchestration

> **Intelligent academic literature search system powered by LangGraph AI, integrating PubMed, Scopus, and Semantic Scholar.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Overview

This application offers **two versions** for academic literature search:

### **1. app.py - Basic Version**
Manual search with optional AI consultation.

**Features:**
- Search across 3 sources: PubMed, Scopus, Semantic Scholar
- AI consultation for search strategy (Gemini)
- Full control: choose AI-optimized or original queries
- Year filters and result quantity control
- Customizable display options

**When to use:** You want full manual control over the search process.

---

### **2. app_langgraph.py - AI Advanced Version ⭐ RECOMMENDED**

Fully automated search with LangGraph AI orchestration.

**Advanced Features:**
- ✅ **Automatic query analysis** (topic, intent, language detection)
- ✅ **Intelligent query optimization** for each source (PubMed MeSH, Scopus syntax)
- ✅ **Parallel async search** - 50% faster
- ✅ **Smart 3-tier deduplication** (DOI → PMID → Title similarity 85%)
- ✅ **30-minute caching** - saves 40% API calls
- ✅ **Auto refinement** (max 2 attempts) when results are insufficient
- ✅ **Project management** - save search history and results
- ✅ **Early stopping** - stops when quality score >= 0.7 or sufficient results found

**When to use:** You want the best results, fastest performance, and full automation.

---

## 📊 Feature Comparison

| Feature | app.py | app_langgraph.py |
|---------|--------|------------------|
| **Query optimization** | ❌ Manual | ✅ AI automatic |
| **Source selection** | ❌ User selects | ✅ AI selects based on topic |
| **Deduplication** | ❌ None | ✅ 3-tier smart deduplication |
| **Caching** | ❌ None | ✅ 30-min TTL cache |
| **Search method** | ❌ Sequential | ✅ Parallel async |
| **Auto refinement** | ❌ None | ✅ Max 2 attempts |
| **Project management** | ❌ None | ✅ Full project tracking |
| **Speed** | 30-45s | ⚡ 15-20s |
| **Resource savings** | None | ✅ ~60% |
| **User steps required** | 3-4 steps | 1 step |

---

## ⚡ Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure API Keys

Create a `.env` file in the root directory:

```bash
GEMINI_API_KEY=your_key_here          # Required for AI features
PUBMED_API_KEY=your_key_here          # Optional (increases rate limit)
SCOPUS_API_KEY=your_key_here          # Required for Scopus
SEMANTIC_SCHOLAR_API_KEY=your_key_here # Optional
```

**Get API Keys:**
- **Gemini AI**: https://aistudio.google.com/ (free)
- **Scopus**: https://dev.elsevier.com/ (requires registration)
- **PubMed**: https://www.ncbi.nlm.nih.gov/account/ (free)
- **Semantic Scholar**: https://www.semanticscholar.org/product/api (free, optional)

### 3️⃣ Run the Application

**LangGraph AI Version (Recommended):**
```bash
./start_langgraph.sh
# Or:
streamlit run app_langgraph.py
```

**Basic Version:**
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

---

## 📖 Usage Guide

### Using app_langgraph.py (AI Version)

1. **Enter your query** (Vietnamese or English)
   ```
   Example: "treatment of hypertension in elderly patients"
   Example: "điều trị tăng huyết áp ở người cao tuổi"
   ```

2. **Configure settings** (sidebar)
   - Filters: publication year range, max results
   - Sources: PubMed, Scopus, Semantic Scholar
   - Display: authors, DOI, abstract, citations, etc.

3. **Click "🚀 Smart Search (LangGraph AI)"**
   - AI automatically analyzes and optimizes your query
   - Parallel search across selected sources
   - Smart deduplication removes duplicates
   - Results displayed in organized tabs

4. **Save to project** (optional)
   - Select articles to save
   - Save to new or existing project
   - Manage projects in sidebar

### Using app.py (Basic Version)

1. **Enter your query**
2. **Click "🤖 AI Consultation"** (optional) → View AI recommendations
3. **Choose:** "Search with AI Query" or "Search with Original Query"
4. **View results** organized by source tabs

---

## 🏗️ Project Structure

```
tim_y_van_04_api/
├── README.md                  # This file
├── app.py                     # Basic search app
├── app_langgraph.py          # LangGraph AI app ⭐
├── start_langgraph.sh        # Quick start script
├── requirements.txt          # Python dependencies
├── .env                      # API keys (create this)
├── .gitignore               # Git ignore rules
├── CHANGELOG.md             # Project history
├── DEPLOYMENT.md            # Streamlit Cloud deployment guide
│
├── .streamlit/              # Streamlit configuration
│   ├── secrets.toml        # API keys for cloud (gitignored)
│   └── config.toml         # Streamlit settings
│
├── backend/                 # Backend logic
│   ├── search_manager.py   # Logic for app.py
│   ├── langgraph_orchestrator.py  # LangGraph workflow
│   ├── gemini_service.py   # Gemini AI service
│   ├── async_apis.py       # Async search + Cache + Deduplication
│   ├── project_manager.py  # Project management
│   ├── state_schema.py     # LangGraph state schema
│   ├── storage.py          # Data persistence
│   ├── pubmed_api.py       # PubMed client
│   ├── scopus_api.py       # Scopus client
│   ├── semantic_scholar_api.py  # Semantic Scholar client
│   └── nodes/              # LangGraph nodes (6 files)
│       ├── analyze.py      # Query analysis
│       ├── plan.py         # Strategy planning
│       ├── optimize.py     # Query optimization
│       ├── execute.py      # Search execution
│       ├── evaluate.py     # Results evaluation & deduplication
│       └── refine.py       # Query refinement
│
├── projects/               # Project data (auto-created)
│   └── projects_registry.json
│
└── docs/                   # Detailed documentation
    ├── README.md          # Documentation index
    ├── FINAL_SUMMARY.md   # LangGraph implementation summary
    ├── COMPARISON.md      # Detailed app comparison
    ├── USAGE_GUIDE.md     # Step-by-step usage guide
    └── LANGGRAPH_README.md # LangGraph technical documentation
```

---

## 🎓 Use Cases

### Case 1: Medical Research (Vietnamese)

```
Query: "Điều trị ung thư phổi giai đoạn muộn"

→ AI analysis: topic=medical, language=vi
→ Sources selected: PubMed + Semantic Scholar
→ PubMed query: "lung cancer[MeSH] AND advanced stage AND treatment"
→ Semantic query: keeps Vietnamese for better local results
→ Results: 45 articles (PubMed: 30, Semantic: 15)
→ After deduplication: 38 unique articles
→ Quality score: 0.85 → STOP ✅
```

### Case 2: Engineering Research (English)

```
Query: "Machine learning in weather forecasting"

→ AI analysis: topic=engineering, language=en
→ Sources selected: Scopus + Semantic Scholar
→ First search: 12 articles (too few)
→ Quality: 0.45 → REFINE 🔄
→ Refined query: "machine learning weather prediction climate"
→ Second search: 78 articles
→ Quality: 0.82 → STOP ✅
```

---

## 🔧 LangGraph AI Workflow

The `app_langgraph.py` uses a sophisticated AI workflow:

```
START
  ↓
[ANALYZE] - Detect topic, language, intent
  ↓
[PLAN] - Select optimal sources
  ↓
[OPTIMIZE] - Create source-specific queries
  ↓
[EXECUTE] - Parallel async search + caching
  ↓
[EVALUATE] - Deduplication + quality scoring
  ↓
 Decision: needs_refinement?
  ├─ No → END ✅
  └─ Yes (& attempts < 2) → [REFINE] → back to OPTIMIZE
```

**Stopping Conditions:**
1. ✅ Quality score >= 0.7
2. ✅ Found >= 80% of requested results
3. ✅ Refinement attempts >= 2

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not found"
- Ensure `.env` file exists in the root directory
- Verify format: `GEMINI_API_KEY=AIzaSy...`
- For Streamlit Cloud, add key to secrets in dashboard

### Error: "Scopus authentication failed"
- Verify Scopus API key is valid
- Check quota at dev.elsevier.com
- Ensure institutional access if required

### Error: "Rate limit exceeded"
- Wait 1-2 minutes before retry
- Add API keys to increase limits:
  - PubMed: 10 req/s (with key) vs 3 req/s (without)
- Use caching feature in `app_langgraph.py`

### No results found
- Try simpler, more general query terms
- Expand year range in filters
- Use AI optimization in `app_langgraph.py`
- Check if selected sources are accessible

### Application won't start
- Verify Python 3.9+ is installed
- Install all requirements: `pip install -r requirements.txt`
- Check for port conflicts (default: 8501)

---

## 🚀 Deployment

### Local Deployment

See [Quick Start](#-quick-start) above.

### Streamlit Community Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions including:
- GitHub setup
- Streamlit Cloud configuration
- Secrets management
- Troubleshooting

**Quick Deploy Steps:**
1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Select repository and `app_langgraph.py`
4. Add API keys to Secrets (TOML format)
5. Deploy!

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit 1.28+
- **AI/ML:**
  - Google Gemini 2.0 Flash (LLM)
  - LangGraph (AI orchestration)
  - LangChain (AI framework)
- **APIs:**
  - NCBI Entrez (PubMed)
  - Elsevier Scopus Search API
  - Semantic Scholar Graph API
- **Language:** Python 3.9+
- **Key Libraries:** `requests`, `python-dotenv`, `google-generativeai`

---

## 📚 Additional Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Streamlit Cloud deployment guide
- [CHANGELOG.md](CHANGELOG.md) - Project history and changes
- [docs/FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) - Complete LangGraph implementation
- [docs/COMPARISON.md](docs/COMPARISON.md) - Detailed feature comparison
- [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - Step-by-step usage instructions
- [docs/LANGGRAPH_README.md](docs/LANGGRAPH_README.md) - LangGraph architecture

---

## 🤝 Contributing

This is an academic project. Contributions and suggestions are welcome:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - Free for academic and research purposes.

See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Data Sources:** PubMed/NCBI, Elsevier Scopus, Semantic Scholar
- **AI Provider:** Google Gemini
- **Framework:** Streamlit, LangGraph, LangChain

---

## 📧 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)
- Open an issue on GitHub

---

**🎉 Happy researching! Start with `app_langgraph.py` for the best experience!**

---

*Last updated: 2025-01-27*
