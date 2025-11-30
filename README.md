# Autonomous Research Agent (Streamlit + Chroma + Tavily + OpenAI)

This project is a starter implementation of an autonomous research agent with:
- Streamlit frontend
- Tavily search integration
- Simple web scraping + cleaning
- Token-aware chunking
- Embeddings via OpenAI
- Local Chroma vector store
- Synthesis via OpenAI ChatCompletion

## What's included
- `app.py` : Streamlit application
- `src/` : modular code (tavily client wrapper, scraper, cleaner, chunker, embedder, chroma store, summarizer)
- `requirements.txt`
- `.env.example`
- `README.md` (this)

## Quick start
1. Clone or unzip the project.
2. Create a Python virtualenv and activate it.
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from `.env.example` and add your keys:
   - TAVILY_API_KEY
   - OPENAI_API_KEY
5. Run Streamlit
   ```bash
   streamlit run app.py
   ```

## Notes
- This is a starter scaffold. Improve scraping, add robust error handling, and rate-limiting for production.
- Model names and APIs may change. If an API call fails, check the provider docs and update model names or client usage.