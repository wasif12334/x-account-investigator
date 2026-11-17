
import re
from collections import Counter, defaultdict


# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    "the", "and", "for", "are", "was", "were",
    "this", "that", "with", "from", "have",
    "has", "had", "you", "your", "they",
    "them", "their", "our", "out", "about",
    "into", "just", "like", "what", "when",
    "where", "who", "why", "how", "will",
    "would", "could", "should", "can", "not",
    "but", "all", "any", "some", "more",
    "very", "also", "been", "being", "its",
    "his", "her", "she", "him", "he",
    "than", "then", "there", "here", "which",
    "while", "after", "before", "over",
    "under", "again", "still", "only",
    "much", "many", "most", "such",
    "get", "got", "getting", "make",
    "made", "making", "one", "two",
    "today", "tomorrow", "yesterday",
    "https", "http", "www", "com",
    "amp", "via", "rt", "says", "said",
    "new", "now", "first", "last",
    "year", "years", "time", "day",
    "week", "month", "according", "report",
    "reports", "breaking", "latest",
    "exclusive", "update", "watch",
    "read", "click", "thread", "post",
    "posts", "link", "three", "may",
    "might", "their", "there",
}


# ============================================================
# TOPIC TAXONOMY
# ============================================================

TOPIC_CATEGORIES = {

    "Finance & Economics": {
        "keywords": [
            "consumer price index",
            "producer price index",
            "federal reserve",
            "central bank",
            "monetary policy",
            "fiscal policy",
            "government debt",
            "national debt",
            "public debt",
            "economic growth",
            "economic slowdown",
            "economic recession",
            "gross domestic product",
            "treasury yields",
            "bond yields",
            "credit markets",
            "credit spreads",
            "credit cycle",
            "banking crisis",
            "bank failures",
            "liquidity crisis",
            "deficit spending",
            "sovereign debt",
            "interest rates",
            "inflation",
            "deflation",
            "disinflation",
            "unemployment",
            "consumer spending",
            "economic data",
            "budget deficit",
            "trade deficit",
            "yield curve",
            "mortgage rates",
            "housing market",
            "money supply",
            "purchasing power",
            "cpi",
            "ppi",
            "gdp",
        ],
        "description": (
            "Coverage of macroeconomic conditions, inflation, "
            "interest rates, central banks, debt, banking and "
            "economic policy."
        ),
    },

    "Financial Markets & Investments": {
        "keywords": [
            "stock market",
            "equity market",
            "equity markets",
            "stock futures",
            "equity futures",
            "stock prices",
            "share prices",
            "wall street",
            "hedge funds",
            "market rally",
            "market selloff",
            "market crash",
            "bear market",
            "bull market",
            "bond market",
            "commodity market",
            "gold prices",
            "silver prices",
            "options trading",
            "short selling",
            "short interest",
            "market volatility",
            "market capitalization",
            "market cap",
            "initial public offering",
            "ipo",
            "nasdaq",
            "s&p 500",
            "dow jones",
            "premarket trading",
            "after hours trading",
            "stock trading",
            "shareholders",
            "institutional investors",
            "retail investors",
            "portfolio allocation",
            "investment portfolio",
            "asset allocation",
            "equity valuations",
            "bond yields",
            "stock index",
            "stock indices",
            "futures market",
            "trading volume",
            "options market",
            "derivatives market",
            "financial markets",
            "investors",
            "investment",
            "trading",
        ],
        "description": (
            "Coverage of stocks, bonds, commodities, market "
            "movements, investment activity and trading."
        ),
    },

    "Politics & Geopolitics": {
        "keywords": [
            "white house",
            "presidential election",
            "foreign policy",
            "geopolitical tensions",
            "international relations",
            "military conflict",
            "military operations",
            "trade war",
            "economic sanctions",
            "political campaign",
            "political party",
            "government policy",
            "donald trump",
            "joe biden",
            "middle east",
            "south china sea",
            "united nations",
            "security council",
            "nato alliance",
            "russia ukraine",
            "ukraine war",
            "iran war",
            "congress",
            "senate",
            "parliament",
            "election",
            "president",
            "geopolitics",
            "geopolitical",
            "sanctions",
            "nato",
            "russia",
            "ukraine",
        ],
        "description": (
            "Coverage of government, elections, international "
            "relations, military developments and geopolitical events."
        ),
    },

    "Business & Corporate News": {
        "keywords": [
            "chief executive officer",
            "quarterly earnings",
            "corporate earnings",
            "company earnings",
            "corporate profits",
            "business growth",
            "corporate restructuring",
            "board of directors",
            "revenue growth",
            "profit margin",
            "private equity",
            "venture capital",
            "merger and acquisition",
            "mergers and acquisitions",
            "company bankruptcy",
            "corporate bankruptcy",
            "business strategy",
            "corporate debt",
            "company shares",
            "executive compensation",
            "corporate governance",
            "earnings report",
            "earnings guidance",
            "ceo",
            "bankruptcy",
            "merger",
            "acquisition",
        ],
        "description": (
            "Coverage of corporate performance, earnings, "
            "executives, business developments and company decisions."
        ),
    },

    "Technology & Artificial Intelligence": {
        "keywords": [
            "artificial intelligence",
            "machine learning",
            "generative ai",
            "large language model",
            "large language models",
            "language model",
            "ai model",
            "ai models",
            "ai infrastructure",
            "ai spending",
            "ai industry",
            "ai chips",
            "ai data center",
            "data center",
            "data centers",
            "semiconductor industry",
            "semiconductor",
            "semiconductors",
            "chipmaker",
            "chipmakers",
            "openai",
            "anthropic",
            "chatgpt",
            "deep learning",
            "computer vision",
            "cloud computing",
            "technology industry",
            "software company",
            "tech industry",
            "artificial neural network",
            "gpu computing",
            "gpu",
        ],
        "description": (
            "Coverage of artificial intelligence, software, "
            "semiconductors, computing infrastructure and "
            "technology developments."
        ),
    },

    "Energy & Commodities": {
        "keywords": [
            "crude oil",
            "oil prices",
            "natural gas",
            "oil production",
            "oil supply",
            "oil demand",
            "energy prices",
            "energy market",
            "energy markets",
            "oil exports",
            "gas prices",
            "energy crisis",
            "renewable energy",
            "coal prices",
            "commodity prices",
            "oil inventories",
            "oil reserves",
            "energy consumption",
            "energy production",
            "oil futures",
            "opec",
            "petroleum",
            "liquefied natural gas",
            "lng",
        ],
        "description": (
            "Coverage of energy markets, oil, natural gas, "
            "commodities, production and energy supply."
        ),
    },

    "Health & Medicine": {
        "keywords": [
            "public health",
            "healthcare system",
            "health care system",
            "medical research",
            "clinical trial",
            "clinical trials",
            "disease outbreak",
            "infectious disease",
            "mental health",
            "health insurance",
            "medical treatment",
            "medical condition",
            "hospital care",
            "vaccine",
            "vaccination",
            "pandemic",
            "epidemic",
            "healthcare",
        ],
        "description": (
            "Coverage of healthcare, medical research, public "
            "health and medical developments."
        ),
    },

    "Sports": {
        "keywords": [
            "football match",
            "cricket match",
            "basketball game",
            "tennis tournament",
            "world cup",
            "champions league",
            "premier league",
            "sports team",
            "football team",
            "cricket team",
            "sports tournament",
            "olympic games",
            "professional football",
        ],
        "description": (
            "Coverage of sporting events, teams, competitions "
            "and professional sports."
        ),
    },

    "Entertainment & Media": {
        "keywords": [
            "box office",
            "television series",
            "film industry",
            "music industry",
            "movie release",
            "streaming service",
            "music album",
            "video game",
            "gaming industry",
            "celebrity news",
            "film release",
        ],
        "description": (
            "Coverage of entertainment, film, music, gaming "
            "and media developments."
        ),
    },
}


# ============================================================
# GET TWEETS
# ============================================================

def get_tweets(state):
    tweets = state.get("tweets")

    if isinstance(tweets, list) and tweets:
        return tweets

    x_data = state.get("x_data") or {}
    tweets = x_data.get("tweets", [])

    return tweets if isinstance(tweets, list) else []


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    # Preserve hashtag words.
    text = re.sub(
        r"#([A-Za-z0-9_]+)",
        r"\1",
        text
    )

    text = re.sub(
        r"[^A-Za-z0-9\s'-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.lower().strip()


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(text):
    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z'-]{2,}\b",
        text
    )

    return [
        word.lower()
        for word in words
        if word.lower() not in STOPWORDS
    ]


# ============================================================
# HASHTAG EXTRACTION
# ============================================================

def extract_hashtags(tweet):
    hashtags = tweet.get("hashtags", [])

    if isinstance(hashtags, str):
        hashtags = [hashtags]

    if not isinstance(hashtags, list):
        hashtags = []

    extracted = []

    for tag in hashtags:
        if isinstance(tag, str):
            tag = tag.strip().lower().lstrip("#")

            if tag:
                extracted.append(tag)

    text = tweet.get("text", "")

    if isinstance(text, str):
        extracted.extend(
            tag.lower()
            for tag in re.findall(
                r"#([A-Za-z0-9_]+)",
                text
            )
        )

    return extracted


# ============================================================
# TOPIC MATCHING
# ============================================================

def match_topics(text):
    """
    Rule-based multi-label classification.

    Specific phrases receive stronger scores.
    Generic single words are not used as independent signals.
    """

    matched_topics = []

    for topic, details in TOPIC_CATEGORIES.items():

        matched_keywords = []
        score = 0

        for keyword in details["keywords"]:

            pattern = (
                r"(?<!\w)"
                + re.escape(keyword.lower())
                + r"(?!\w)"
            )

            if not re.search(pattern, text):
                continue

            matched_keywords.append(keyword)

            if len(keyword.split()) >= 2:
                score += 2
            else:
                score += 1

        # A single specific multi-word phrase can qualify.
        # A single generic word cannot qualify on its own.
        if score >= 2:
            matched_topics.append({
                "topic": topic,
                "score": score,
                "matched_keywords": matched_keywords,
                "description": details["description"],
            })

    return sorted(
        matched_topics,
        key=lambda item: item["score"],
        reverse=True
    )


# ============================================================
# TOPIC AGENT
# ============================================================

def topic_agent(state):

    print("\n      Running Topics & Interests Analysis...")

    tweets = get_tweets(state)

    keyword_counter = Counter()
    hashtag_counter = Counter()
    topic_counter = Counter()

    topic_keywords = defaultdict(Counter)
    topic_examples = defaultdict(list)

    analyzed_tweets = 0
    classified_tweet_ids = set()

    # --------------------------------------------------------
    # PROCESS TWEETS
    # --------------------------------------------------------

    for index, tweet in enumerate(tweets):

        if not isinstance(tweet, dict):
            continue

        original_text = tweet.get("text", "")

        if not isinstance(original_text, str):
            continue

        if not original_text.strip():
            continue

        analyzed_tweets += 1

        cleaned_text = clean_text(original_text)

        # ----------------------------------------------------
        # KEYWORDS
        # ----------------------------------------------------

        keywords = extract_keywords(cleaned_text)

        # Count a keyword once per tweet.
        keyword_counter.update(set(keywords))

        # ----------------------------------------------------
        # HASHTAGS
        # ----------------------------------------------------

        hashtag_counter.update(
            set(extract_hashtags(tweet))
        )

        # ----------------------------------------------------
        # TOPICS
        # ----------------------------------------------------

        matched_topics = match_topics(cleaned_text)

        if matched_topics:
            classified_tweet_ids.add(index)

        for item in matched_topics:

            topic = item["topic"]

            topic_counter[topic] += 1

            topic_keywords[topic].update(
                item["matched_keywords"]
            )

            # Store examples with their classification score.
            topic_examples[topic].append({
                "score": item["score"],
                "text": original_text.strip(),
                "matched_keywords": item["matched_keywords"],
            })

    # --------------------------------------------------------
    # CLASSIFICATION COVERAGE
    # --------------------------------------------------------

    classified_tweets = len(classified_tweet_ids)

    unclassified_tweets = max(
        analyzed_tweets - classified_tweets,
        0
    )

    coverage = (
        classified_tweets / analyzed_tweets * 100
        if analyzed_tweets else 0
    )

    # --------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------

    top_keywords = [
        {
            "keyword": word,
            "count": count,
        }
        for word, count in keyword_counter.most_common(20)
    ]

    # --------------------------------------------------------
    # HASHTAGS
    # --------------------------------------------------------

    hashtags = [
        {
            "hashtag": tag,
            "count": count,
        }
        for tag, count in hashtag_counter.most_common(20)
    ]

    # --------------------------------------------------------
    # TOPIC GROUPS
    # --------------------------------------------------------

    topic_groups = []

    for topic, count in topic_counter.most_common():

        details = TOPIC_CATEGORIES[topic]

        ranked_examples = sorted(
            topic_examples[topic],
            key=lambda item: item["score"],
            reverse=True
        )

        representative_tweets = []
        seen_examples = set()

        for example in ranked_examples:

            example_text = example["text"]

            if example_text in seen_examples:
                continue

            seen_examples.add(example_text)

            representative_tweets.append({
                "text": (
                    example_text[:297] + "..."
                    if len(example_text) > 300
                    else example_text
                ),
                "score": example["score"],
                "matched_keywords": example["matched_keywords"],
            })

            if len(representative_tweets) >= 5:
                break

        topic_groups.append({
            "topic": topic,
            "tweet_count": count,

            # Denominator is all analyzed tweets.
            # Multi-label percentages may overlap.
            "percentage": round(
                count / analyzed_tweets * 100,
                2
            ) if analyzed_tweets else 0,

            "description": details["description"],

            "supporting_keywords": [
                {
                    "keyword": keyword,
                    "count": keyword_count,
                }
                for keyword, keyword_count
                in topic_keywords[topic].most_common(10)
            ],

            "representative_tweets": representative_tweets,
        })

    # --------------------------------------------------------
    # PRIMARY AND SECONDARY INTERESTS
    # --------------------------------------------------------

    primary_interests = []
    secondary_interests = []

    for index, topic in enumerate(topic_groups):

        interest = {
            "topic": topic["topic"],
            "tweet_count": topic["tweet_count"],
            "percentage": topic["percentage"],
            "description": topic["description"],
        }

        if index == 0:
            primary_interests.append(interest)
        else:
            secondary_interests.append(interest)

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {
        "status": (
            "success"
            if analyzed_tweets
            else "not_available"
        ),

        "tweets_received": len(tweets),

        "tweets_analyzed": analyzed_tweets,

        "classified_tweets": classified_tweets,

        "unclassified_tweets": unclassified_tweets,

        "classification_coverage_percentage": round(
            coverage,
            2
        ),

        "topics_detected": len(topic_groups),

        "analysis_method": (
            "Rule-based multi-label topic classification "
            "using phrase matching, weighted evidence, "
            "and ranked representative examples."
        ),

        "percentage_note": (
            "Topic percentages use all analyzed tweets as "
            "the denominator. A tweet may belong to multiple "
            "topics, so topic percentages can overlap."
        ),

        "message": (
            "Topic analysis completed."
            if analyzed_tweets
            else "No valid tweet text was available."
        ),

        "top_keywords": top_keywords,

        "hashtags": hashtags,

        "topic_groups": topic_groups,

        "primary_interests": primary_interests,

        "secondary_interests": secondary_interests,
    }

    # --------------------------------------------------------
    # CONSOLE SUMMARY
    # --------------------------------------------------------

    print("\n      ---------- TOPIC ANALYSIS ----------")

    print(f"      Tweets received: {len(tweets)}")

    print(f"      Tweets analyzed: {analyzed_tweets}")

    print(f"      Classified tweets: {classified_tweets}")

    print(f"      Unclassified tweets: {unclassified_tweets}")

    print(f"      Classification coverage: {coverage:.2f}%")

    print(f"      Topics detected: {len(topic_groups)}")

    for topic in topic_groups:
        print(
            f"      {topic['topic']}: "
            f"{topic['tweet_count']} tweets "
            f"({topic['percentage']}%)"
        )

    print("      ------------------------------------")

    return {
        "topic_analysis": result
    }
