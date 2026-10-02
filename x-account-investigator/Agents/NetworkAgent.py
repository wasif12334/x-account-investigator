from collections import Counter


def network_agent(state):

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

    # No tweet data
    if not tweets:

        if tweets_status == "rate_limited":

            return {
                "network_analysis": {
                    "status": "rate_limited",
                    "summary": (
                        "Network analysis could not be performed "
                        "because tweet collection was temporarily "
                        "unavailable."
                    ),
                    "mentioned_accounts": [],
                    "interaction_count": 0
                }
            }

        return {
            "network_analysis": {
                "status": "not_analyzed",
                "summary": (
                    "Network analysis was not performed because "
                    "no tweet dataset was available."
                ),
                "mentioned_accounts": [],
                "interaction_count": 0
            }
        }

    mentions = []

    for tweet in tweets:

        tweet_mentions = tweet.get(
            "user_mentions",
            []
        )

        mentions.extend(
            tweet_mentions
        )

    mention_counts = Counter(
        mentions
    )

    top_accounts = [
        {
            "username": username,
            "count": count
        }

        for username, count
        in mention_counts.most_common(10)
    ]

    return {
        "network_analysis": {
            "status": "success",

            "total_tweets_analyzed": len(
                tweets
            ),

            "mentioned_accounts": top_accounts,

            "interaction_count": len(
                mentions
            ),

            "summary": (
                f"{len(tweets)} tweets were analyzed. "
                f"{len(mentions)} public account mentions "
                f"were identified."
            )
        }
    }