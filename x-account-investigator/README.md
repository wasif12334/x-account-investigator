# 🚀 X Account Investigator

X Account Investigator is an AI-powered multi-agent OSINT system that analyzes publicly available information from X (Twitter) and Wikipedia to generate structured investigation reports.

The project uses LangGraph, twscrape, Wikipedia, and AI agents to investigate account activity, profile information, interaction patterns, topics, and publicly available identity signals.

---

# ⚡ Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/wasif12334/x-account-investigator.git
cd x-account-investigator
```

## 2. Create Virtual Environment

```bash
uv venv
```

Activate:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
groq_ai_key=your_groq_ai_key
```

---

## 5. Configure twscrape (One-Time Setup)

This project uses the open-source **twscrape** library to collect publicly available X data.

Add an X account:

```bash
twscrape add_accounts accounts.txt
```

Login:

```bash
twscrape login_accounts
```

Verify:

```bash
twscrape accounts
```

This setup is only required once. twscrape stores and reuses login sessions automatically.

---

## 6. Run the Project

```bash
python main.py
```

or

```bash
uv run python main.py
```

Enter an X username when prompted:

```text
Enter X username:
```

Example:

```text
elonmusk
```

The investigation will start automatically and generate a PDF report.

---

# 🔍 Investigation Pipeline

The investigation follows a LangGraph workflow:

```text
User Input
    │
    ▼
Wikipedia Agent
    │
    ▼
X Scraper (twscrape)
    │
    ▼
Profile Agent
    │
    ▼
Network Agent
    │
    ▼
Temporal Agent
    │
    ▼
Topic Agent
    │
    ▼
Verification Agent
    │
    ▼
Report Agent
    │
    ▼
PDF Investigation Report
```

### Wikipedia Agent

Searches Wikipedia for matching entities and gathers publicly available background information.

### X Scraper

Collects:

* Profile metadata
* Followers count
* Following count
* Account creation date
* Recent tweets

### Profile Agent

Analyzes account profile information and metadata.

### Network Agent

Analyzes mentions and interaction patterns.

### Temporal Agent

Analyzes posting behavior and activity timing.

### Topic Agent

Identifies:

* Keywords
* Hashtags
* Languages
* Content signals

### Verification Agent

Reviews evidence, identifies limitations, and evaluates cross-source consistency.

### Report Agent

Generates a structured investigation report and exports a professional PDF with charts and summaries.

---

# 🏗 Architecture

```text
User Input
     │
     ▼
LangGraph Workflow
     │
     ├── Wikipedia Agent
     ├── X Scraper
     ├── Profile Agent
     ├── Network Agent
     ├── Temporal Agent
     ├── Topic Agent
     ├── Verification Agent
     └── Report Agent
                │
                ▼
         PDF Report
```
