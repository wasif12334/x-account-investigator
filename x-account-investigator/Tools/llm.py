import asyncio
import re
from typing import Any, Dict, List

from twscrape import API, AccountsPool


MAX_TWEETS = 500


def extract_profile(user) -> Dict[str, Any]:
    """Convert twscrape User object into a clean dictionary."""

    return {
        "username": getattr(user, "username", "") or "",
        "display_name": getattr(user, "displayname", "") or "",
        "bio": getattr(user, "rawDescription", "") or "",
        "location": getattr(user, "location", "") or "",
        "followers": getattr(user, "followersCount", 0) or 0,
        "following": getattr(user, "friendsCount", 0) or 0,
        "tweets_count": getattr(user, "statusesCount", 0) or 0,
        "verified": bool(getattr(user, "verified", False)),
        "created": str(getattr(user, "created", "") or ""),
        "profile_url": (
            f"https://x.com/{getattr(user, 'username', '')}"
            if getattr(user, "username", "")
            else ""
        ),
    }


def normalize_tweet(tweet) -> Dict[str, Any]:
    """Convert a twscrape Tweet object into a stable dictionary."""

    text = (
        getattr(tweet, "rawContent", None)
        or getattr(tweet, "text", None)
        or ""
    )

    username = ""

    tweet_user = getattr(tweet, "user", None)

    if tweet_user:
        username = (
            getattr(tweet_user, "username", None)
            or ""
        )

    if not username:
        username = getattr(tweet, "username", "") or ""

    hashtags = getattr(tweet, "hashtags", None) or []

    if not hashtags:
        hashtags = re.findall(r"#([A-Za-z0-9_]+)", text)

    mentions = getattr(tweet, "mentionedUsers", None) or []

    mention_names = []

    for user in mentions:
        if isinstance(user, str):
            mention_names.append(user)
        else:
            username_value = getattr(user, "username", None)
            if username_value:
                mention_names.append(username_value)

    if not mention_names:
        mention_names = re.findall(
            r"@([A-Za-z0-9_]+)",
            text
        )

    # Reply information
    reply_to_tweet = (
        getattr(tweet, "inReplyToTweetId", None)
        or getattr(tweet, "in_reply_to_tweet_id", None)
    )

    reply_to_user = (
        getattr(tweet, "inReplyToUser", None)
        or getattr(tweet, "in_reply_to_user", None)
    )

    if reply_to_user and not isinstance(reply_to_user, str):
        reply_to_user = (
            getattr(reply_to_user, "username", None)
            or ""
        )

    # Quote information
    quoted_tweet = (
        getattr(tweet, "quotedTweet", None)
        or getattr(tweet, "quoted_tweet", None)
    )

    quoted_user = ""

    if quoted_tweet:
        quoted_user_obj = getattr(
            quoted_tweet,
            "user",
            None
        )

        if quoted_user_obj:
            quoted_user = (
                getattr(
                    quoted_user_obj,
                    "username",
                    None
                )
                or ""
            )

    # Retweet information
    retweeted_tweet = (
        getattr(tweet, "retweetedTweet", None)
        or getattr(tweet, "retweeted_tweet", None)
    )

    retweeted_user = ""

    if retweeted_tweet:
        retweeted_user_obj = getattr(
            retweeted_tweet,
            "user",
            None
        )

        if retweeted_user_obj:
            retweeted_user = (
                getattr(
                    retweeted_user_obj,
                    "username",
                    None
                )
                or ""
            )

    date_value = (
        getattr(tweet, "date", None)
        or getattr(tweet, "created", None)
        or ""
    )

    return {
        "id": str(getattr(tweet, "id", "") or ""),
        "text": text,
        "date": str(date_value),
        "username": username,

        "hashtags": hashtags,
        "mentions": mention_names,

        "in_reply_to_tweet_id": (
            str(reply_to_tweet)
            if reply_to_tweet
            else ""
        ),

        "in_reply_to_user": reply_to_user or "",

        "quoted_user": quoted_user,

        "retweeted_user": retweeted_user,

        "is_reply": bool(reply_to_tweet),
        "is_quote": bool(quoted_tweet),
        "is_retweet": bool(
            retweeted_tweet
            or re.match(
                r"^\s*RT\s+@",
                text,
                re.IGNORECASE
            )
        ),
    }


async def collect_tweets(api, user_id: int) -> tuple:
    """
    Collect tweets while preserving partial results.

    Returns:
        tweets, status, message
    """

    tweets: List[Dict[str, Any]] = []

    try:
        async for tweet in api.user_tweets(
            user_id,
            limit=MAX_TWEETS
        ):
            tweets.append(
                normalize_tweet(tweet)
            )

            if len(tweets) >= MAX_TWEETS:
                break

        if tweets:
            return (
                tweets,
                "success",
                f"{len(tweets)} tweets collected successfully."
            )

        return (
            [],
            "error",
            "No tweets were returned."
        )

    except Exception as exc:

        if tweets:
            return (
                tweets,
                "partial",
                (
                    f"Tweet collection stopped after "
                    f"{len(tweets)} tweets: {exc}"
                )
            )

        return (
            [],
            "error",
            f"Tweet collection failed: {exc}"
        )


async def scrape_x_account(handle: str) -> Dict[str, Any]:
    """Scrape one X account."""

    handle = handle.strip().lstrip("@")

    if not handle:
        return {
            "status": "error",
            "profile_status": "error",
            "tweet_status": "error",
            "profile": {},
            "tweets": [],
            "requested_tweets": MAX_TWEETS,
            "tweets_collected": 0,
            "message": "Empty X handle."
        }

    print(f"      Looking up X account: @{handle}")

    api = API(AccountsPool())

    try:
        user = await api.user_by_login(handle)

    except Exception as exc:

        return {
            "status": "not_found",
            "profile_status": "error",
            "tweet_status": "error",
            "profile": {},
            "tweets": [],
            "requested_tweets": MAX_TWEETS,
            "tweets_collected": 0,
            "message": f"X profile lookup failed: {exc}"
        }

    if not user:

        return {
            "status": "not_found",
            "profile_status": "error",
            "tweet_status": "error",
            "profile": {},
            "tweets": [],
            "requested_tweets": MAX_TWEETS,
            "tweets_collected": 0,
            "message": f"X account @{handle} was not found."
        }

    profile = extract_profile(user)

    print(
        f"      X profile found: "
        f"@{profile['username']} "
        f"({profile['display_name']})"
    )

    print()
    print("      ---------- X PROFILE DATA ----------")
    print(f"      Username:   {profile['username']}")
    print(f"      Name:       {profile['display_name']}")
    print(f"      Bio:        {profile['bio']}")
    print(f"      Location:   {profile['location']}")
    print(f"      Followers:  {profile['followers']}")
    print(f"      Following:  {profile['following']}")
    print(f"      Tweets:     {profile['tweets_count']}")
    print(f"      Verified:   {profile['verified']}")
    print(f"      Created:    {profile['created']}")
    print(f"      URL:        {profile['profile_url']}")
    print("      -------------------------------------")

    tweets, tweet_status, message = await collect_tweets(
        api,
        user.id
    )

    if tweet_status == "success":
        overall_status = "success"
    elif tweet_status == "partial":
        overall_status = "partial"
    else:
        overall_status = "partial" if profile else "error"

    print()
    print("      ---------- X COLLECTION ----------")
    print(f"      Collection status: {overall_status}")
    print("      Profile status: success")
    print(f"      Tweet status: {tweet_status}")
    print(f"      Tweets requested: {MAX_TWEETS}")
    print(f"      Tweets collected: {len(tweets)}")
    print("      ----------------------------------")

    result = {
        "status": overall_status,

        "profile_status": "success",

        "tweet_status": tweet_status,

        "profile": profile,

        "tweets": tweets,

        "requested_tweets": MAX_TWEETS,

        "tweets_collected": len(tweets),

        "message": message,
    }

    return result


def x_scraper_node(state):

    handle = (
        state.get("discovered_handle")
        or state.get("username")
        or ""
    )

    print(
        f"      Collecting data for: "
        f"@{handle}"
    )

    if not handle:
        return {
            "x_data": {
                "status": "error",
                "profile": {},
                "tweets": [],
                "tweets_collected": 0,
                "message": "No discovered X handle."
            },
            "tweets": [],
        }

    result = asyncio.run(
        scrape_x_account(handle)
    )

    # IMPORTANT:
    # Put tweets in BOTH locations.
    # This prevents downstream agents from losing them.

    return {
        "x_data": result,

        "tweets": result.get(
            "tweets",
            []
        ),

        "profile": result.get(
            "profile",
            {}
        ),
    }