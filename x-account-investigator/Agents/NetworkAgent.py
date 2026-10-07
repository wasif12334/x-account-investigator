import re
from collections import Counter
from typing import Any, Dict, List


def get_tweets(state) -> List[Dict[str, Any]]:
    """
    Get tweets from the normalized top-level state first.
    Fall back to x_data for compatibility.
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

def network_agent(state):

    tweets = state.get("x_data", {}).get(
        "tweets",
        []
    )

    if not tweets:

        state["network_analysis"] = {
            "status": "not_available",
            "tweets_analyzed": 0,
            "mentioned_accounts": [],
            "interaction_count": 0,
            "reason": (
                "No tweets available."
            )
        }

        return state

    mentions = {}

    for tweet in tweets:

        text = getattr(
            tweet,
            "rawContent",
            ""
        )

        for word in text.split():

            if word.startswith("@"):

                username = word.lower()

                mentions[username] = (
                    mentions.get(username, 0)
                    + 1
                )

    top_mentions = sorted(
        mentions.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]

    state["network_analysis"] = {
        "status": "analyzed",
        "tweets_analyzed": len(tweets),
        "unique_accounts": len(mentions),
        "interaction_count": sum(
            mentions.values()
        ),
        "top_mentions": top_mentions
    }

    return state