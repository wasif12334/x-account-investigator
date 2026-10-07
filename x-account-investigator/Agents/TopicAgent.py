import re
from collections import Counter
from typing import Any, Dict, List


STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "this",
    "with",
    "from",
    "you",
    "your",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "will",
    "would",
    "could",
    "should",
    "about",
    "into",
    "than",
    "then",
    "they",
    "them",
    "their",
    "there",
    "here",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "how",
    "more",
    "some",
    "very",
    "just",
    "also",
    "been",
    "being",
    "its",
    "it's",
    "our",
    "out",
    "not",
    "but",
    "can",
    "all",
    "get",
    "got",
    "like",
    "one",
    "two",
    "new",
    "now",
    "today",
    "via",
    "http",
    "https",
    "www",
    "com",
    "account",
    "accounts",
    "thank",
}


def get_tweets(state) -> List[Dict[str, Any]]:

    tweets = state.get("tweets")

    if isinstance(tweets, list):
        return tweets

    x_data = state.get(
        "x_data",
        {}
    )

    if isinstance(x_data, dict):

        tweets = x_data.get(
            "tweets",
            []
        )

        if isinstance(tweets, list):
            return tweets

    return []


def clean_text(text: str) -> str:

    text = re.sub(
        r"https?://\S+",
        " ",
        text
    )

    text = re.sub(
        r"www\.\S+",
        " ",
        text
    )

    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    text = re.sub(
        r"#(\w+)",
        r" \1 ",
        text
    )

    return text


def topic_agent(state):

    tweets = get_tweets(state)

    print(
        f"      Topic analysis received "
        f"{len(tweets)} tweets."
    )

    keyword_counter = Counter()
    hashtag_counter = Counter()

    target = (
        state.get(
            "person_name",
            ""
        )
        .lower()
        .replace(
            " ",
            ""
        )
    )

    for tweet in tweets:

        if not isinstance(tweet, dict):
            continue

        text = clean_text(
            tweet.get(
                "text",
                ""
            )
        )

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z'-]{2,}\b",
            text.lower()
        )

        for word in words:

            normalized = (
                word
                .strip("-'")
                .lower()
            )

            if (
                normalized in STOPWORDS
                or normalized == target
                or len(normalized) < 3
            ):
                continue

            keyword_counter[
                normalized
            ] += 1

        hashtags = tweet.get(
            "hashtags",
            []
        )

        for hashtag in hashtags:

            hashtag = str(
                hashtag
            ).strip().lstrip("#").lower()

            if hashtag:
                hashtag_counter[
                    f"#{hashtag}"
                ] += 1

    analysis = {
        "tweets_analyzed":
            len(tweets),

        "top_keywords":
            [
                {
                    "keyword": word,
                    "count": count
                }
                for word, count
                in keyword_counter.most_common(20)
            ],

        "hashtags":
            [
                {
                    "hashtag": tag,
                    "count": count
                }
                for tag, count
                in hashtag_counter.most_common(20)
            ],
    }

    print(
        "      Topic analysis completed."
    )

    return {
        "topic_analysis":
            analysis
    }