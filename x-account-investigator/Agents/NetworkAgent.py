
import re
from collections import Counter
from typing import Any, Dict, List, Optional


# ==========================================================
# Tweet Retrieval
# ==========================================================

def get_tweets(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieve normalized tweets from the LangGraph state.

    Expected normalized tweet structure:

    {
        "id": "...",
        "text": "...",
        "date": "...",
        "username": "...",
        "hashtags": [...],
        "mentions": [...]
    }
    """

    tweets = state.get("tweets")

    if isinstance(tweets, list):
        return tweets

    x_data = state.get("x_data", {})

    if isinstance(x_data, dict):
        tweets = x_data.get("tweets", [])

        if isinstance(tweets, list):
            return tweets

    return []


# ==========================================================
# Utility Functions
# ==========================================================

def safe_int(value: Any) -> Optional[int]:
    """Convert a value to an integer safely."""

    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def extract_text(tweet: Dict[str, Any]) -> str:
    """Extract tweet text from supported field names."""

    for field in ("text", "rawContent", "full_text"):
        value = tweet.get(field)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return ""


def normalize_username(value: Any) -> Optional[str]:
    """
    Normalize a username.

    Supports:
        "@username"
        "username"
        {"username": "username"}
        {"screen_name": "username"}
    """

    if isinstance(value, dict):
        value = (
            value.get("username")
            or value.get("screen_name")
            or value.get("screenName")
            or value.get("name")
        )

    if not isinstance(value, str):
        return None

    username = value.strip().lower()

    if username.startswith("@"):
        username = username[1:]

    if not username:
        return None

    if not re.fullmatch(r"[a-z0-9_]{1,15}", username):
        return None

    return username


def extract_mentions(tweet: Dict[str, Any]) -> List[str]:
    """
    Extract mentioned usernames.

    Priority:
    1. Normalized mentions field.
    2. Text-based @username extraction.

    This prevents double-counting when the scraper already
    provides structured mention metadata.
    """

    mentions = tweet.get("mentions")

    if isinstance(mentions, list) and mentions:

        extracted = []

        for mention in mentions:

            username = normalize_username(mention)

            if username:
                extracted.append(username)

        if extracted:
            return extracted

    text = extract_text(tweet)

    if not text:
        return []

    # Match actual @username patterns.
    # Avoid matching email addresses.
    matches = re.findall(
        r"(?<![\w@])@([A-Za-z0-9_]{1,15})\b",
        text
    )

    return [
        username.lower()
        for username in matches
    ]


# ==========================================================
# Reply Detection
# ==========================================================

def is_reply(tweet: Dict[str, Any]) -> bool:
    """
    Detect replies only when explicit reply metadata exists.

    Missing metadata is not treated as proof that a tweet
    is not a reply.
    """

    reply_fields = (
        "in_reply_to_username",
        "in_reply_to_user_id",
        "inReplyToUsername",
        "inReplyToUserId",
        "in_reply_to_status_id",
        "inReplyToTweetId"
    )

    for field in reply_fields:

        if tweet.get(field) is not None:
            return True

    return False


# ==========================================================
# Retweet and Quote Detection
# ==========================================================

def get_reference_types(tweet: Dict[str, Any]) -> List[str]:
    """Extract reference types from normalized tweet metadata."""

    references = tweet.get("referenced_tweets", [])

    if not isinstance(references, list):
        return []

    reference_types = []

    for reference in references:

        if not isinstance(reference, dict):
            continue

        reference_type = (
            reference.get("type")
            or reference.get("referenced_type")
        )

        if isinstance(reference_type, str):
            reference_types.append(reference_type.lower())

    return reference_types


def is_retweet(tweet: Dict[str, Any]) -> bool:
    """Detect retweets using explicit metadata."""

    reference_types = get_reference_types(tweet)

    if "retweeted" in reference_types:
        return True

    if isinstance(tweet.get("retweeted_status"), dict):
        return True

    if tweet.get("is_retweet") is True:
        return True

    return False


def is_quote(tweet: Dict[str, Any]) -> bool:
    """Detect quote posts using explicit metadata."""

    reference_types = get_reference_types(tweet)

    if "quoted" in reference_types:
        return True

    if isinstance(tweet.get("quoted_status"), dict):
        return True

    if tweet.get("is_quote") is True:
        return True

    return False


# ==========================================================
# Main Network Analysis Agent
# ==========================================================

def network_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze tweet mentions and available interaction metadata.

    Returns a partial LangGraph state update.

    Important:
    - Mentions are extracted from structured metadata or text.
    - Replies, retweets and quotes are counted only when
      explicit metadata is available.
    - Missing metadata is reported as unavailable rather
      than being presented as confirmed zero activity.
    """

    tweets = get_tweets(state)

    if not tweets:

        return {
            "network_analysis": {
                "status": "not_available",
                "tweets_analyzed": 0,
                "unique_accounts": 0,
                "unique_mentioned_accounts": 0,
                "mentioned_accounts": [],
                "top_mentions": [],
                "interaction_count": 0,
                "mention_count": 0,
                "replies": None,
                "retweets": None,
                "quotes": None,
                "metadata_availability": {
                    "mentions": False,
                    "replies": False,
                    "retweets": False,
                    "quotes": False
                },
                "reason": "No tweets available."
            }
        }

    # ------------------------------------------------------
    # Counters
    # ------------------------------------------------------

    mention_counter = Counter()

    replies_count = 0
    retweets_count = 0
    quotes_count = 0

    reply_metadata_available = False
    retweet_metadata_available = False
    quote_metadata_available = False
    mention_metadata_available = False

    analyzed_tweets = 0

    # ------------------------------------------------------
    # Process Tweets
    # ------------------------------------------------------

    for tweet in tweets:

        if not isinstance(tweet, dict):
            continue

        analyzed_tweets += 1

        # Mentions
        structured_mentions = tweet.get("mentions")

        if isinstance(structured_mentions, list) and structured_mentions:
            mention_metadata_available = True

        extracted_mentions = extract_mentions(tweet)

        for username in extracted_mentions:
            mention_counter[username] += 1

        # Replies
        reply_fields = (
            "in_reply_to_username",
            "in_reply_to_user_id",
            "inReplyToUsername",
            "inReplyToUserId",
            "in_reply_to_status_id",
            "inReplyToTweetId"
        )

        if any(tweet.get(field) is not None for field in reply_fields):
            reply_metadata_available = True

        if is_reply(tweet):
            replies_count += 1

        # Retweets
        if (
            "referenced_tweets" in tweet
            or "retweeted_status" in tweet
            or "is_retweet" in tweet
        ):
            retweet_metadata_available = True

        if is_retweet(tweet):
            retweets_count += 1

        # Quotes
        if (
            "referenced_tweets" in tweet
            or "quoted_status" in tweet
            or "is_quote" in tweet
        ):
            quote_metadata_available = True

        if is_quote(tweet):
            quotes_count += 1

    # ------------------------------------------------------
    # Results
    # ------------------------------------------------------

    top_mentions = mention_counter.most_common(20)

    mentioned_accounts = [
        {
            "username": username,
            "mention_count": count
        }
        for username, count in top_mentions
    ]

    unique_accounts = len(mention_counter)

    total_mentions = sum(mention_counter.values())

    # Only calculate interaction totals when the relevant
    # metadata is available. Mentions are independently
    # observable from tweet text.
    available_interactions = total_mentions

    if reply_metadata_available:
        available_interactions += replies_count

    if retweet_metadata_available:
        available_interactions += retweets_count

    if quote_metadata_available:
        available_interactions += quotes_count

    result = {
        "status": "analyzed",

        "tweets_analyzed": analyzed_tweets,

        # Mention statistics
        "unique_accounts": unique_accounts,
        "unique_mentioned_accounts": unique_accounts,
        "mentioned_accounts": mentioned_accounts,
        "top_mentions": top_mentions,
        "mention_count": total_mentions,

        # Compatibility field
        "interaction_count": available_interactions,

        # Interaction statistics
        "replies": replies_count if reply_metadata_available else None,
        "retweets": retweets_count if retweet_metadata_available else None,
        "quotes": quotes_count if quote_metadata_available else None,

        # Metadata availability
        "metadata_availability": {
            "mentions": mention_metadata_available or total_mentions > 0,
            "replies": reply_metadata_available,
            "retweets": retweet_metadata_available,
            "quotes": quote_metadata_available
        },

        "analysis_note": (
            "Mentions were extracted from structured metadata "
            "or tweet text. Replies, retweets and quotes are "
            "counted only when their corresponding metadata "
            "is available. Unavailable metrics are reported "
            "as None, not as confirmed zero."
        )
    }

    # ------------------------------------------------------
    # Console Output
    # ------------------------------------------------------

    print("\n---------- NETWORK ANALYSIS ----------")

    print(f"Tweets analyzed: {analyzed_tweets}")

    print(f"Unique mentioned accounts: {unique_accounts}")

    print(f"Total mentions: {total_mentions}")

    print(
        "Replies:",
        replies_count if reply_metadata_available else "Metadata unavailable"
    )

    print(
        "Retweets:",
        retweets_count if retweet_metadata_available else "Metadata unavailable"
    )

    print(
        "Quotes:",
        quotes_count if quote_metadata_available else "Metadata unavailable"
    )

    print("\nTop mentioned accounts:")

    if top_mentions:

        for username, count in top_mentions:
            print(f"  @{username}: {count}")

    else:
        print("  No mentions detected.")

    print("--------------------------------------\n")

    return {
        "network_analysis": result
    }
