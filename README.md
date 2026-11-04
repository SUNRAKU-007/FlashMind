# FlashMind

A multi-agent research system with a Streamlit UI. Give it a topic and four specialised AI agents search the web, read the best source, write a structured report and critique it.

<!-- Add a screenshot here: save it as assets/screenshot.png, then uncomment the next line -->
<!-- ![FlashMind UI](assets/screenshot.png) -->

## How it works

```mermaid
flowchart LR
    A[Topic] --> B[Search Agent]
    B --> C[Reader Agent]
    C --> D[Writer Chain]
    D --> E[Critic Chain]
    E --> F[Report + Score]
```

| Step | Component | What it does |
|------|-----------|--------------|
| 1 | **Search Agent** | Uses the `web_search` tool to find recent, relevant sources |
| 2 | **Reader Agent** | Picks the best URL and scrapes it with the `scrape_url` tool |
| 3 | **Writer Chain** | Turns the gathered research into a structured, cited report |
| 4 | **Critic Chain** | Reviews the report and gives a score, strengths and weaknesses |

The agents are built with LangChain's `create_agent`. The writer and critic are LCEL chains (`prompt | llm | StrOutputParser()`). All steps run on Google Gemini.

## Features

- Live pipeline view: each step shows Waiting, Running or Done, with timings
- Final report with introduction, key findings, limitations, conclusion and sources
- Critic feedback with a score out of 10
- Stats for total time, report length, sources cited and critic score
- Tabs for the raw search results and scraped content, including tool calls
- Run history in the sidebar
- Download the report as Markdown

## Tech stack

Python, LangChain, LangGraph, Google Gemini (`langchain-google-genai`), Tavily search, BeautifulSoup, Streamlit

## Project structure

```
FlashMind/
├── app.py             # Streamlit UI
├── pipeline.py        # agents and chains (search, reader, writer, critic)
├── tools.py           # web_search and scrape_url tools
├── requirements.txt
├── .env.example       # template for your API keys
└── README.md
```

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/SUNRAKU-007/FlashMind.git
cd FlashMind
```

**2. Create and activate a virtual environment**

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API keys**

Copy the template and fill in your own keys:

```bash
cp .env.example .env
```

On Windows PowerShell use `copy .env.example .env`.

```
GOOGLE_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
```

Get a Gemini key from [Google AI Studio](https://aistudio.google.com/) and a Tavily key from [tavily.com](https://tavily.com/).

**5. Run the app**

```bash
streamlit run app.py
```

It opens at `http://localhost:8501`.

## Usage

1. Type a research topic, or click one of the example chips.
2. Click **Run research pipeline** and watch the four steps run.
3. Read the report, check the critic's feedback, and download the Markdown file.

## Limitations

- The reader agent scrapes one page per run, so the report depends heavily on that source.
- Some sites block scraping, which can leave thin content for the writer.
- The critic is another LLM pass. It does not verify sources, so check important claims yourself.

## Roadmap

- [ ] Scrape several sources per run
- [ ] Stream the report as it is written
- [ ] Export to PDF
- [ ] Add source-quality scoring

## Author

**Manjot Singh** · [GitHub](https://github.com/SUNRAKU-007)
