from collections import Counter
import re


def topic_agent(state):

    x_data = state.get(
        "x_data",
        {}
    )

    tweets = x_data.get(
        "tweets",
        []
    )

    tweets_status = x_data.get(
        "tweets_status",
        "unknown"
    )

    if not tweets:

        if tweets_status == "rate_limited":

            return {
                "topic_analysis": {
                    "status": "rate_limited",

                    "summary": (
                        "Topic analysis could not be performed "
                        "because tweet collection was temporarily "
                        "unavailable."
                    ),

                    "hashtags": [],
                    "keywords": [],
                    "languages": {}
                }
            }

        return {
            "topic_analysis": {
                "status": "not_analyzed",

                "summary": (
                    "Topic analysis was not performed because "
                    "no tweet content was collected."
                ),

                "hashtags": [],
                "keywords": [],
                "languages": {}
            }
        }

    hashtags = []

    words = []

    languages = []

    stop_words = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "will",
        "your",
        "about",
        "what",
        "when",
        "where",
        "which",
        "their",
        "there",
        "they",
        "been",
        "were",
        "would",
        "could",
        "should",
        "into",
        "than",
        "then",
        "also",
        "just",
        "more",
        "very",
        "some"
    }

    for tweet in tweets:

        tweet_hashtags = tweet.get(
            "hashtags",
            []
        )

        hashtags.extend(
            tweet_hashtags
        )

        language = tweet.get(
            "lang"
        )

        if language:

            languages.append(
                language
            )

        text = tweet.get(
            "text",
            ""
        ).lower()

        text = re.sub(
            r"https?://\S+",
            "",
            text
        )

        found_words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            text
        )

        words.extend(
            word
            for word in found_words
            if word not in stop_words
        )

    hashtag_counts = Counter(
        hashtags
    )

    word_counts = Counter(
        words
    )

    language_counts = Counter(
        languages
    )

    common_hashtags = [
        {
            "hashtag": tag,
            "count": count
        }

        for tag, count
        in hashtag_counts.most_common(10)
    ]

    common_keywords = [
        {
            "keyword": word,
            "count": count
        }

        for word, count
        in word_counts.most_common(20)
    ]

    return {
        "topic_analysis": {

            "status": "success",

            "hashtags": common_hashtags,

            "keywords": common_keywords,

            "languages": dict(
                language_counts
            ),

            "summary": (
                f"{len(tweets)} tweets were analyzed "
                "for hashtags, keywords and languages."
            )
        }
    }