from collections import Counter
from datetime import datetime


def temporal_agent(state):

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
                "temporal_analysis": {
                    "status": "rate_limited",
                    "summary": (
                        "Temporal analysis could not be performed "
                        "because tweet collection was temporarily "
                        "unavailable."
                    )
                }
            }

        return {
            "temporal_analysis": {
                "status": "not_analyzed",
                "summary": (
                    "Temporal analysis was not performed because "
                    "no tweet timestamps were collected."
                )
            }
        }

    hours = []

    days = []

    valid_dates = 0

    for tweet in tweets:

        date_text = tweet.get(
            "date"
        )

        if not date_text:
            continue

        try:

            date = datetime.fromisoformat(
                date_text.replace(
                    "Z",
                    "+00:00"
                )
            )

            hours.append(
                date.hour
            )

            days.append(
                date.strftime("%A")
            )

            valid_dates += 1

        except Exception:
            continue

    if not hours:

        return {
            "temporal_analysis": {
                "status": "insufficient_data",

                "summary": (
                    f"{len(tweets)} tweets were collected, "
                    "but usable timestamps were not available."
                )
            }
        }

    hour_counts = Counter(
        hours
    )

    day_counts = Counter(
        days
    )

    most_active_hour = (
        hour_counts.most_common(1)[0][0]
    )

    most_active_day = (
        day_counts.most_common(1)[0][0]
    )

    return {
        "temporal_analysis": {

            "status": "success",

            "total_tweets": len(
                tweets
            ),

            "timestamps_analyzed": valid_dates,

            "most_active_hour": (
                f"{most_active_hour}:00"
            ),

            "most_active_day": (
                most_active_day
            ),

            "hour_distribution": dict(
                hour_counts
            ),

            "day_distribution": dict(
                day_counts
            ),

            "summary": (
                f"Among the collected tweets with usable "
                f"timestamps, the highest observed activity "
                f"occurred around {most_active_hour}:00 "
                f"on {most_active_day}."
            )
        }
    }