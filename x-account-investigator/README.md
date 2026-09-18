# 🚀 How the Project Works

The X Account Investigator is an AI-powered multi-agent system that investigates publicly available information about an X (Twitter) account.

The investigation process follows these steps:

1. The user provides an X username.
2. The Profile Analyzer collects account information.
3. The Activity Analyzer examines recent activity and topics.
4. The Identity OSINT Agent searches public sources to identify the person or organization behind the account.
5. The Evidence Verifier reviews all findings and checks for inconsistencies.
6. The Report Agent generates the final investigation report.

---

# 📂 Project Structure

```text
x-account-investigator/
│
├── main.py                    # Main entry point
├── .env                       # API Keys
│
├── Agents/
│   ├── BaseAgent.py
│   ├── ProfileAnalyzer.py
│   ├── ActivityAnalyzer.py
│   ├── IdentityOSINTAgent.py
│   ├── EvidenceVerifier.py
│   └── ReportAgent.py
│
├── Models/
│   └── schemas.py
│
└── requirements.txt
```

---

# ▶️ Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python main.py
```

or

```bash
uv run python main.py
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root directory:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

# 🎯 Changing the X Account

Open:

```text
main.py
```

Locate the username variable:

```python
username = "Cristiano"
```

Replace it with any X username:

```python
username = "elonmusk"
```

or

```python
username = "OpenAI"
```

Save the file and run the project again.

---

# 🤖 AI Model Configuration

Open:

```text
Agents/BaseAgent.py
```

Locate:

```python
model="gemini-2.5-flash"
```

Change it to any supported Gemini model if needed.
