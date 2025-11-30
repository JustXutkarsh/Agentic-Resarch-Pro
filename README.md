🤝 Agentic Research PRO
Autonomous Multi-Agent Research System powered by LLMs, Web Search, Retrieval and PDF Export

Agentic Research PRO is a full multi-agent pipeline that automates deep research.
It combines search, scraping, chunking, embedding, retrieval, reasoning, and report generation — just like a real research analyst team.

This is not a prompt wrapper.
This is a modular, agent-driven system with clean pipelines, semantic chunking, vector search and structured output.

🧠 How It Works

Agentic Research PRO runs an end-to-end research workflow:

Web Search → Scraper → Chunker → Embedder → VectorDB → Retriever → Writer → PDF Export


Each step is handled by its own agent:

Agent	Description
Web Search Agent	Uses Tavily API to fetch high-quality search results
Scraper Agent	Fetches article text, auto-cleans it (HTML → clean text)
Chunker Agent	Splits long text into overlapping semantic chunks
Embedding Agent	Converts chunks into vectors using OpenAI embeddings
Vector Store Agent	Stores vectors in ChromaDB for retrieval
Retrieval Agent	Finds the most relevant text for the research topic
Writer Agent	Uses GPT to generate a structured research report
PDF Export Agent	Converts final research into a downloadable PDF
✨ Features

🔍 Real-time web search (Tavily API)

📰 Article scraping + auto-cleaning

✂️ Smart chunking for long text

🧠 Embedding + Vector search

🔎 Evidence-based retrieval

📝 Structured report generation

📄 PDF export with source links

🔗 Clickable URLs in UI + PDF

⚡ Mac-optimized + Memory-safe scraping

🚀 Tech Stack
Component	Technology
Frontend	Streamlit
LLM	GPT-4o / GPT-4.1 mini
Search	Tavily API
Scraping	Newspaper3k + Requests + BeautifulSoup
Vector DB	ChromaDB (persistent local DB)
Embeddings	OpenAI Text Embeddings 3 Large
PDF Export	FPDF
Environment Management	python-dotenv
📦 Installation (Mac-friendly)
1) Clone the repo
git clone https://github.com/yourusername/agentic-research-pro.git
cd agentic-research-pro

2) Create a virtual environment
python3 -m venv venv
source venv/bin/activate

3) Install dependencies
pip install -r requirements.txt

4) Install additional Mac-required libraries
pip install newspaper3k
python3 -m nltk.downloader punkt

🔐 Environment Variables

Create a .env file:

OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_key

▶️ Run the app
streamlit run app.py


Your app will open at:

http://localhost:8501

📁 Project Structure
root
│── app.py
│── requirements.txt
│── .env.example
│── research_report.pdf (auto-exported)
│
└── src/
    ├── scraper.py
    ├── chunker.py
    ├── embedder.py
    ├── chroma_store.py
    ├── summarizer.py
    ├── cleaner.py

🧩 Requirements File

Example requirements.txt:

streamlit
openai
tavily-python
newspaper3k
beautifulsoup4
requests
python-dotenv
chromadb
fpdf
nltk

🛠 Troubleshooting (Mac)
❗ “Your system ran out of application memory”

Scraping + embeddings too large.
Fix: chunking now capped + safe scraper included.

❗ ChromaDB legacy error

We use the new chromadb.PersistentClient format.

❗ Newspaper3k errors

Run:

pip install newspaper3k
python3 -m nltk.downloader punkt

🧭 Roadmap

 Multi-modal agents

 Interactive citations

 Browser agent with Playwright

 PDF ingestion + hybrid RAG

 Research reasoning graphs

 Multi-topic batch mode
