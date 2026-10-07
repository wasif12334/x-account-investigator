# 🚀 X Account Investigator

**X Account Investigator** is an AI-powered multi-agent OSINT system that analyzes publicly available information from **X (Twitter)** and **Wikipedia** to investigate a person, organization, or public entity.

The system uses **LangGraph**, **twscrape**, **Wikipedia**, and AI-powered analysis agents to discover likely X accounts, analyze profile information, study tweet activity, identify topics and interaction patterns, verify identity signals, and generate a structured investigation report in PDF format.

> ⚠️ **Important:** This project is intended for research, educational, and authorized OSINT use. It analyzes publicly available information and does not guarantee account ownership or identity.

---

# ✨ Features

* 👤 Accepts a **person/entity name** instead of requiring an X username
* 📚 Searches Wikipedia before X investigation
* 🔎 Discovers likely X accounts automatically
* 🐦 Uses the open-source **twscrape** library for X data collection
* 👤 Extracts X profile metadata
* 🕸️ Analyzes mentions and interaction patterns
* ⏱️ Analyzes temporal posting activity
* 🏷️ Extracts keywords and hashtags
* 🔐 Performs cross-source identity verification
* 📊 Generates a structured investigation report
* 📄 Generates a PDF investigation report
* 🛡️ Preserves partial tweet data if collection is interrupted
* ⏳ Uses a timeout so the investigation does not wait indefinitely for an unavailable twscrape account
* 🧩 Uses LangGraph for multi-agent orchestration

---

# 🏗️ Investigation Pipeline

The current investigation workflow is:

```text
Person / Entity Name
        │
        ▼
Wikipedia Agent
        │
        ▼
X Account Discovery
        │
        ▼
X Scraper (twscrape)
        │
        ▼
Profile Analysis
        │
        ├──────────────┐
        ▼              ▼
Network          Temporal
Analysis         Analysis
        │              │
        └──────┬───────┘
               ▼
         Topic Analysis
               │
               ▼
       Verification Agent
               │
               ▼
         Report Agent
               │
               ▼
      Final Report + PDF
```

---

# 🔍 How the Investigation Works

## 1. Person / Entity Input

The application asks for a name:

```text
Enter person's name:
```

Example:

```text
The Daily Show
```

or:

```text
Elon Musk
```

You do **not** need to provide the X username manually.

---

## 2. Wikipedia Agent

The Wikipedia Agent runs first.

It searches Wikipedia for the supplied name and attempts to identify the correct entity.

For example:

```text
Searching Wikipedia for: The Daily Show

Wikipedia exact match: The Daily Show
Wikipedia analysis completed.
```

The collected information is later used as identity/context evidence during X account discovery and verification.

---

# 3. X Account Discovery

After Wikipedia, the system searches for possible X accounts.

The discovery system:

* Generates possible username candidates
* Searches X for additional candidates
* Validates candidate accounts
* Compares display names
* Compares usernames
* Uses Wikipedia identity information
* Scores candidate accounts
* Selects the strongest candidate

Example:

```text
Generated handle candidates: 7
X user search candidates: 20
Total candidates: 27

Checking @theshow...
Checking @the_show...
Checking @thedailyshow...
...

Best candidate: @TheDailyShow
Confidence: 70/100
Discovery status: LIKELY
```

The discovered account is then passed automatically to the scraper.

---

# 4. X Scraper

The project uses **twscrape**, an open-source Python library, to collect publicly available X data.

The scraper collects:

### Profile information

* Username
* Display name
* Bio
* Location
* Followers
* Following
* Post count
* Verification indicator
* Account creation date
* Profile URL

### Tweet information

The scraper attempts to collect up to:

```text
500 tweets
```

The actual number may be lower because X request limits and twscrape account availability can affect collection.

For example:

```text
Tweets requested: 500
Tweets collected: 391
```

This is considered a valid **partial collection**.

---

# 🔑 Setting Up twscrape

The X scraper requires at least one X account configured through twscrape.

This is a **one-time setup**.

## Step 1 — Create an X Account

Use an X account that you are authorized to use for this project.

You can use a normal X account for twscrape.

It is recommended to use a dedicated research/testing account rather than your primary personal account.

> Do not use someone else's account or credentials without permission.

---

# Step 2 — Create `accounts.txt`

Inside your project directory, create:

```text
accounts.txt
```

Add your X login information in the format expected by your installed twscrape version.

A common format is:

```text
username:password
```

Example:

```text
my_research_account:your_password
```

If your X account uses additional authentication such as email verification or two-factor authentication, twscrape may require the corresponding information during account login/setup depending on the version and X authentication flow.

**Do not commit `accounts.txt` to GitHub.**

Add it to `.gitignore`:

```gitignore
accounts.txt
.env
```

---

# Step 3 — Add the Account to twscrape

Activate your virtual environment first.

### Windows

```powershell
.venv\Scripts\activate
```

Then:

```bash
twscrape add_accounts accounts.txt
```

You should see the account being added to the twscrape account pool.

---

# Step 4 — Login the Account

Run:

```bash
twscrape login_accounts
```

twscrape will attempt to authenticate the account.

If additional authentication is required, follow the prompts provided by twscrape/X.

---

# Step 5 — Check Account Status

Run:

```bash
twscrape accounts
```

You want to see an account that is logged in and available.

For example:

```text
username             logged_in    active
-----------------------------------------
my_research_account  True         True
```

The exact output can vary between twscrape versions.

The important thing is that the account is successfully logged in and available to the account pool.

---

# 🐦 How twscrape Works in This Project

The project initializes:

```python
API(AccountsPool())
```

This means twscrape manages the configured X accounts through its account pool.

When the application requests tweets, twscrape selects an available account.

The project does **not** require you to manually enter the X account every time you investigate someone.

Once the twscrape account is configured, the application automatically uses the account pool.

---

# ⚠️ X Rate Limits and Account Availability

X can temporarily restrict requests.

You may see a message similar to:

```text
No account available for queue "UserTweets".
Next available at ...
```

This means twscrape currently does not have an account available for that operation.

The scraper in this project has a timeout mechanism.

Instead of waiting indefinitely, tweet collection eventually stops and the investigation continues.

For example:

```text
Attempting to collect up to 500 tweets...
Tweet collection timeout: 15 seconds

Tweet collection stopped: Tweet collection timed out.
Preserving 391 tweets.
```

The final report will then indicate:

```text
Collection Status: partial
Tweets Collected: 391
```

This is intentional.

The project preserves successfully collected data instead of discarding it.

---

# 🛠️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/wasif12334/x-account-investigator.git
```

Move into the project:

```bash
cd x-account-investigator
```

---

# 2. Create Virtual Environment

Using `uv`:

```bash
uv venv
```

---

# 3. Activate Virtual Environment

## Windows PowerShell

```powershell
.venv\Scripts\activate
```

## Windows CMD

```cmd
.venv\Scripts\activate
```

## Linux / macOS

```bash
source .venv/bin/activate
```

---

# 4. Install Dependencies

Install the project dependencies:

```bash
uv pip install -r requirements.txt
```

If you are using the project's existing `pyproject.toml`, you can also use the appropriate `uv` project installation workflow.

---

# 🔐 Environment Variables

Create a file named:

```text
.env
```

in the project root.

Add your Groq API key:

```env
groq_ai_key=your_groq_ai_key
```

Example:

```env
groq_ai_key=gsk_xxxxxxxxxxxxxxxxx
```

> Never commit `.env` to GitHub.

Add this to `.gitignore`:

```gitignore
.env
```

---

# ▶️ Running the Project

After installing the dependencies and configuring twscrape, run:

```bash
python main.py
```

or:

```bash
uv run python main.py
```

---

# 🧪 Example Investigation

Run:

```bash
python main.py
```

The application will display:

```text
============================================================
X ACCOUNT INVESTIGATOR
============================================================

Enter person's name:
```

Enter:

```text
The Daily Show
```

The system will then execute:

```text
Person Name
    ↓
Wikipedia
    ↓
X Account Discovery
    ↓
X Scraper
    ↓
Profile / Network / Temporal / Topic
    ↓
Verification
    ↓
Final Report + PDF
```

---

# 📊 Example Console Output

A successful investigation may look similar to:

```text
Enter person's name: The Daily Show

Target person: The Daily Show

Investigation pipeline:
  Person Name
      ↓
  Wikipedia
      ↓
  X Account Discovery
      ↓
  X Scraper
      ↓
  Profile / Network / Temporal / Topic
      ↓
  Verification
      ↓
  Final Report + PDF

Running LangGraph investigation...
Please wait...

Searching Wikipedia for: The Daily Show
Wikipedia exact match: The Daily Show

Discovering X account for: The Daily Show

Best candidate: @TheDailyShow
Confidence: 70/100

Looking up X account: @TheDailyShow

X profile found: @TheDailyShow (The Daily Show)

Attempting to collect up to 500 tweets...

Tweets collected: 391

Profile analysis completed.
Topic analysis completed.
Verification completed.

Generating final investigation report...

PDF report created:
reports/output/the_daily_show_investigation_report.pdf
```

---

# 📁 Generated Reports

PDF reports are generated inside:

```text
reports/output/
```

For example:

```text
reports/
└── output/
    └── the_daily_show_investigation_report.pdf
```

The report contains sections such as:

```text
1. Executive Summary
2. Wikipedia Identity
3. X Account Discovery
4. X Profile
5. Data Collection
6. Network Analysis
7. Temporal Activity
8. Topics & Interests
9. Identity Verification
10. Sources
11. Limitations
```

---

# 🤖 Agents

## Wikipedia Agent

Responsible for:

* Searching Wikipedia
* Finding matching entities
* Extracting background information
* Providing identity/context information

---

## X Discovery Agent

Responsible for:

* Generating possible handles
* Searching X
* Comparing candidate accounts
* Scoring candidates
* Selecting the most likely account

---

## X Scraper

Powered by:

```text
twscrape
```

Responsible for:

* X profile collection
* Tweet collection
* Tweet normalization
* Partial data preservation
* Handling temporary account availability problems

---

## Profile Agent

Analyzes:

* Display name
* Username
* Bio
* Followers
* Following
* Account age
* Verification indicator
* Other profile metadata

---

## Network Agent

Analyzes available interaction signals such as:

* Mentions
* Mentioned accounts
* Replies
* Retweets
* Quotes

The results represent the collected sample and should not be interpreted as a complete social-network graph.

---

## Temporal Agent

Analyzes:

* Tweet timestamps
* Posting hours
* Posting days
* Activity distribution

If timestamps cannot be reliably parsed, the system reports:

```text
Not available
```

rather than inventing an activity pattern.

---

## Topic Agent

Analyzes tweet content for:

* Keywords
* Hashtags
* Repeated terms
* Content themes
* Topic signals

Example:

```text
trump
show
interview
tonight
politics
jon
```

---

## Verification Agent

Compares information from multiple sources.

Possible signals include:

* Wikipedia identity
* X display name
* X username
* Profile metadata
* Bio
* Tweet content
* Verification indicator
* Other publicly available signals

The verification result is an evidence-based assessment and **does not guarantee account ownership**.

---

## Report Agent

Combines the investigation results into a structured report.

It generates:

```text
Final Investigation Report
        +
PDF Report
```

---

# 🏛️ Project Architecture

```text
x-account-investigator/
│
├── Agents/
│   ├── WikipediaAgent.py
│   ├── XDiscoveryAgent.py
│   ├── Profile_Analyzer.py
│   ├── NetworkAgent.py
│   ├── TemporalAgent.py
│   ├── TopicAgent.py
│   ├── VerificationAgent.py
│   └── ReportAgent.py
│
├── Tools/
│   └── x_scraper_tool.py
│
├── graph/
│   └── state.py
│
├── reports/
│   └── output/
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── .env
└── README.md
```

---

# 🔄 LangGraph State

The investigation state passes information between agents.

Conceptually:

```text
{
    username,
    wikipedia_data,
    wikipedia_analysis,
    x_data,
    profile_analysis,
    network_analysis,
    temporal_analysis,
    topic_analysis,
    verification_analysis,
    final_report,
    report_file
}
```

Each agent reads the information it needs and adds its analysis to the shared investigation state.

---

# 🧰 Technology Stack

| Technology | Purpose                                |
| ---------- | -------------------------------------- |
| Python     | Core programming language              |
| LangGraph  | Agent workflow/orchestration           |
| LangChain  | LLM integration and agent tooling      |
| twscrape   | X data collection                      |
| Wikipedia  | Public identity/background information |
| Groq       | LLM inference                          |
| ReportLab  | PDF report generation                  |
| dotenv     | Environment configuration              |

---

# 🔒 Privacy & Security

Never commit sensitive credentials.

Your `.gitignore` should contain at least:

```gitignore
.env
accounts.txt
.venv/
__pycache__/
*.pyc
```

Do not upload:

* X passwords
* Session credentials
* API keys
* Authentication tokens
* Private account information

---

# ⚠️ Limitations

The system has several important limitations:

* X data availability depends on X and twscrape.
* Tweet collection may be partial.
* X request/rate limits can affect collection.
* A configured twscrape account may temporarily become unavailable.
* The collected tweets are only a sample of the account's historical activity.
* Network analysis is not a complete social graph.
* Topic analysis depends on the collected tweets.
* Temporal analysis depends on successfully parsed timestamps.
* Wikipedia information may be incomplete or outdated.
* Matching a name or username does not prove identity.
* The verification score is an evidence-based assessment, not proof of account ownership.
* Public information can change between investigation runs.

---

# 🛡️ Responsible Use

This project should only be used for:

* Educational research
* OSINT research
* Security research
* Public-information analysis
* Authorized investigations
* Academic projects

Do not use the system to:

* Access private accounts
* Obtain unauthorized credentials
* Circumvent authentication
* Harass or target individuals
* Conduct unauthorized surveillance
* Violate X or other platform rules

Always respect applicable laws, platform policies, and the rights of individuals.

---

# 🚀 Quick Start Summary

For an existing installation:

```bash
cd x-account-investigator
```

Activate the environment:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Configure:

```text
.env
accounts.txt
```

Add the twscrape account:

```bash
twscrape add_accounts accounts.txt
```

Login:

```bash
twscrape login_accounts
```

Check:

```bash
twscrape accounts
```

Then run:

```bash
python main.py
```

Enter:

```text
The Daily Show
```

The system will automatically:

```text
Wikipedia
   ↓
X Account Discovery
   ↓
X Scraper
   ↓
Profile Analysis
   ↓
Network Analysis
   ↓
Temporal Analysis
   ↓
Topic Analysis
   ↓
Verification
   ↓
PDF Report
```

---

# 📄 Output

Generated reports can be found in:

```text
reports/output/
```

Example:

```text
reports/output/the_daily_show_investigation_report.pdf
```

---

# 👨‍💻 Author

**Wasif Awan**

Software Engineering Student | AI Engineer | Full-Stack Developer

GitHub:

```text
https://github.com/wasif12334
```

Project:

```text
https://github.com/wasif12334/x-account-investigator
```
