from collections import Counter
from datetime import datetime
from typing import Any, Dict, List


DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def get_tweets(state) -> List[Dict[str, Any]]:

    tweets = state.get("tweets")

    if isinstance(tweets, list):
        return tweets

    x_data = state.get("x_data", {})

    if isinstance(x_data, dict):

        tweets = x_data.get(
            "tweets",
            []
        )

        if isinstance(tweets, list):
            return tweets

    return []


def parse_date(value):

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    # ISO format
    try:
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )
    except ValueError:
        pass

    # Common fallback formats
    formats = [
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%a %b %d %H:%M:%S %z %Y",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value,
                fmt
            )
        except ValueError:
            continue

    return None


def temporal_agent(state):

    tweets = state.get(
        "x_data",
        {}
    ).get(
        "tweets",
        []
    )

    if not tweets:

        state["temporal_analysis"] = {
            "status": "not_available",
            "tweets_analyzed": 0
        }

        return state

    hours = Counter()
    days = Counter()

    for tweet in tweets:

        date = getattr(
            tweet,
            "date",
            None
        )

        if not date:
            continue

        hours[date.hour] += 1

        days[
            date.strftime("%A")
        ] += 1

    state["temporal_analysis"] = {
        "status": "analyzed",
        "tweets_analyzed": len(tweets),
        "hour_distribution": dict(hours),
        "day_distribution": dict(days),
        "most_active_hour":
            max(hours, key=hours.get)
            if hours else None,
        "most_active_day":
            max(days, key=days.get)
            if days else None
    }

    return state