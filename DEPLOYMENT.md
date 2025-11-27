# Deployment Guide - Streamlit Community Cloud

This guide explains how to deploy the Academic Search Assistant to Streamlit Community Cloud.

## Prerequisites

1. GitHub account
2. Streamlit Community Cloud account (free at https://streamlit.io/cloud)
3. Your API keys ready:
   - GEMINI_API_KEY
   - PUBMED_API_KEY (optional)
   - SCOPUS_API_KEY (optional)
   - SEMANTIC_SCHOLAR_API_KEY (optional)

## Local Development

The app works with **two methods** for API key configuration:

### Method 1: Using `.env` file (Local Development)
Create a `.env` file in the root directory with your API keys:
```
GEMINI_API_KEY=your_key_here
PUBMED_API_KEY=your_key_here
SCOPUS_API_KEY=your_key_here
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

### Method 2: Using Streamlit Secrets (Local + Cloud)
The `.streamlit/secrets.toml` file can also be used locally:
```toml
GEMINI_API_KEY = "your_key_here"
PUBMED_API_KEY = "your_key_here"
SCOPUS_API_KEY = "your_key_here"
SEMANTIC_SCHOLAR_API_KEY = "your_key_here"
```

**Note:** The app will try `.env` first, then fall back to `secrets.toml`.

## Deployment Steps

### 1. Push to GitHub

Make sure your code is pushed to a GitHub repository. The `.gitignore` file already excludes:
- `.env` (contains your local API keys)
- `.streamlit/` (contains secrets)

### 2. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set the main file path: `app_langgraph.py` (or `app.py` for the basic version)
6. Click "Advanced settings"

### 3. Configure Secrets

In the "Secrets" section of Advanced settings, paste your API keys in TOML format:

```toml
GEMINI_API_KEY = "AIzaSyAEUwY1fPT1qcdIJ76MdDahQCZ4c-hOQvQ"
PUBMED_API_KEY = "8f6309a1dad8025841e5ff61a0ba78f43908"
SCOPUS_API_KEY = "f863f4a74c34d9ce9f16b13db58d8a42"
SEMANTIC_SCHOLAR_API_KEY = "qpENWNNwbF6iJZcJDT7ekaVNZEqWqlCn4rV5OehO"
```

**Important:** Replace these with your actual API keys!

### 4. Deploy

Click "Deploy!" and wait for the app to build and start.

## App Versions

### LangGraph AI Version (Recommended)
- **File:** `app_langgraph.py`
- **Features:** AI orchestration, automatic query optimization, smart deduplication
- **Requirements:** Gemini API key is mandatory

### Basic Version
- **File:** `app.py`
- **Features:** Simple search with AI consultation
- **Requirements:** Gemini API key for AI features (optional)

## Requirements

Make sure your `requirements.txt` includes all necessary packages:
```
streamlit
python-dotenv
google-generativeai
requests
langchain
langchain-google-genai
langgraph
```

## Troubleshooting

### API Keys Not Working
- Verify the secrets are in correct TOML format
- Check for quotes around string values
- Ensure no trailing spaces or special characters

### App Won't Start
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` includes all dependencies
- Ensure Python version is compatible (3.9+)

### Slow Performance
- Consider upgrading to Streamlit Cloud Teams for better resources
- Reduce `max_results` in the settings
- Disable unused data sources (Scopus if no API key)

## File Structure

```
.
├── app_langgraph.py          # Main LangGraph app
├── app.py                    # Basic app
├── backend/                  # Backend services
├── .streamlit/
│   ├── secrets.toml         # Local secrets (gitignored)
│   └── config.toml          # Streamlit configuration
├── .env                     # Local environment (gitignored)
├── .gitignore               # Git ignore rules
└── requirements.txt         # Python dependencies
```

## Security Notes

- Never commit `.env` or `.streamlit/secrets.toml` to GitHub
- Use different API keys for development and production
- Regularly rotate your API keys
- Monitor API usage to detect unauthorized access

## Support

For issues:
1. Check Streamlit Cloud logs
2. Review this deployment guide
3. Check the main README.md for app documentation
