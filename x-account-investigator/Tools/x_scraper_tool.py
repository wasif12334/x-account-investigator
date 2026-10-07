import asyncio
import re
from typing import Any, Dict, List, Tuple

from twscrape import API, AccountsPool


# =============================================================
# CONFIGURATION
# =============================================================

MAX_TWEETS = 500

# Maximum time allowed for tweet collection.
#
# If twscrape has no available account and starts waiting,
# this timeout stops the wait and allows the investigation
# pipeline to continue.
TWEET_COLLECTION_TIMEOUT = 15


# =============================================================
# SAFE FIELD ACCESS
# =============================================================

def get_user_field(user, *names, default=None):

    for name in names:

        try:
            value = getattr(user, name)

            if value is not None:
                return value

        except Exception:
            pass

    return default


def get_tweet_field(tweet, *names, default=None):

    for name in names:

        try:
            value = getattr(tweet, name)

            if value is not None:
                return value

        except Exception:
            pass

    return default


# =============================================================
# SAFE STRING
# =============================================================

def safe_string(value):

    if value is None:
        return ""

    try:
        return str(value).strip()

    except Exception:
        return ""


# =============================================================
# PROFILE EXTRACTION
# =============================================================

def extract_profile(user):

    username = safe_string(
        get_user_field(
            user,
            "username",
            default=""
        )
    )

    display_name = safe_string(
        get_user_field(
            user,
            "displayname",
            "display_name",
            default=""
        )
    )

    bio = safe_string(
        get_user_field(
            user,
            "rawDescription",
            "description",
            default=""
        )
    )

    location = safe_string(
        get_user_field(
            user,
            "location",
            default=""
        )
    )

    followers = get_user_field(
        user,
        "followersCount",
        "followers_count",
        default=0
    )

    following = get_user_field(
        user,
        "friendsCount",
        "following_count",
        default=0
    )

    tweets_count = get_user_field(
        user,
        "statusesCount",
        "statuses_count",
        default=0
    )

    verified = get_user_field(
        user,
        "verified",
        default=False
    )

    created = get_user_field(
        user,
        "created",
        default=None
    )

    profile_url = (
        f"https://x.com/{username}"
        if username
        else ""
    )

    return {
        "username": username,
        "display_name": display_name,
        "bio": bio,
        "location": location,
        "followers": followers or 0,
        "following": following or 0,
        "tweets_count": tweets_count or 0,
        "verified": bool(verified),
        "created": (
            str(created)
            if created
            else ""
        ),
        "profile_url": profile_url,
    }


# =============================================================
# TWEET NORMALIZATION
# =============================================================

def normalize_tweet(tweet):
    """
    Convert a raw twscrape Tweet object into a simple
    dictionary that all downstream agents can understand.

    Output:

    {
        "id": "...",
        "text": "...",
        "date": "...",
        "username": "...",
        "hashtags": [...],
        "mentions": [...]
    }
    """

    # ---------------------------------------------------------
    # TEXT
    # ---------------------------------------------------------

    text = safe_string(
        get_tweet_field(
            tweet,
            "rawContent",
            "text",
            default=""
        )
    )

    # ---------------------------------------------------------
    # ID
    # ---------------------------------------------------------

    tweet_id = safe_string(
        get_tweet_field(
            tweet,
            "id",
            default=""
        )
    )

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    date = get_tweet_field(
        tweet,
        "date",
        default=None
    )

    # ---------------------------------------------------------
    # USERNAME
    # ---------------------------------------------------------

    user_value = get_tweet_field(
        tweet,
        "user",
        default=""
    )

    username = ""

    if hasattr(
        user_value,
        "username"
    ):

        username = safe_string(
            getattr(
                user_value,
                "username",
                ""
            )
        )

    else:

        username = safe_string(
            user_value
        )

    # ---------------------------------------------------------
    # HASHTAGS
    # ---------------------------------------------------------

    hashtags = re.findall(
        r"#([A-Za-z0-9_]+)",
        text
    )

    # ---------------------------------------------------------
    # MENTIONS
    # ---------------------------------------------------------

    mentions = re.findall(
        r"@([A-Za-z0-9_]+)",
        text
    )

    # ---------------------------------------------------------
    # RETURN NORMALIZED TWEET
    # ---------------------------------------------------------

    return {
        "id": tweet_id,

        "text": text,

        "date": (
            str(date)
            if date
            else ""
        ),

        "username": username,

        "hashtags": hashtags,

        "mentions": mentions,
    }


# =============================================================
# PRINT PROFILE
# =============================================================

def print_profile_summary(profile):

    print(
        "\n      ---------- X PROFILE DATA ----------"
    )

    print(
        f"      Username:   "
        f"{profile.get('username', '')}"
    )

    print(
        f"      Name:       "
        f"{profile.get('display_name', '')}"
    )

    print(
        f"      Bio:        "
        f"{profile.get('bio', '')}"
    )

    print(
        f"      Location:   "
        f"{profile.get('location', '')}"
    )

    print(
        f"      Followers:  "
        f"{profile.get('followers', 0)}"
    )

    print(
        f"      Following:  "
        f"{profile.get('following', 0)}"
    )

    print(
        f"      Tweets:     "
        f"{profile.get('tweets_count', 0)}"
    )

    print(
        f"      Verified:   "
        f"{profile.get('verified', False)}"
    )

    print(
        f"      Created:    "
        f"{profile.get('created', '')}"
    )

    print(
        f"      URL:        "
        f"{profile.get('profile_url', '')}"
    )

    print(
        "      -------------------------------------"
    )


# =============================================================
# RAW TWEET COLLECTION
# =============================================================

async def _collect_tweets_raw(
    api,
    user_id,
    limit=MAX_TWEETS
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Collect tweets from twscrape.

    Every tweet is normalized immediately.

    This means Network, Temporal and Topic agents receive
    dictionaries instead of raw twscrape objects.
    """

    tweets = []

    try:

        async for tweet in api.user_tweets(
            user_id,
            limit=limit
        ):

            try:

                normalized = normalize_tweet(
                    tweet
                )

                tweets.append(
                    normalized
                )

            except Exception as normalize_error:

                print(
                    f"      Tweet normalization warning: "
                    f"{normalize_error}"
                )

                # Do not discard all previously collected
                # tweets because one tweet failed.
                continue

    except asyncio.CancelledError:

        return (
            tweets,
            "Tweet collection timed out."
        )

    except Exception as exc:

        return (
            tweets,
            safe_string(exc)
        )

    return (
        tweets,
        ""
    )


# =============================================================
# COLLECT TWEETS WITH TIMEOUT
# =============================================================

async def collect_tweets(
    api,
    user_id,
    limit=MAX_TWEETS
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Collect tweets with a hard timeout.

    This prevents twscrape from blocking the entire
    investigation when no account is available.
    """

    print(
        f"      Attempting to collect up to "
        f"{limit} tweets..."
    )

    print(
        f"      Tweet collection timeout: "
        f"{TWEET_COLLECTION_TIMEOUT} seconds"
    )

    try:

        tweets, error = await asyncio.wait_for(
            _collect_tweets_raw(
                api,
                user_id,
                limit
            ),
            timeout=TWEET_COLLECTION_TIMEOUT
        )

        return (
            tweets,
            error
        )

    except asyncio.TimeoutError:

        print(
            "\n      ⚠️ Tweet collection timed out."
        )

        print(
            "      twscrape may be waiting for "
            "an available X account."
        )

        print(
            "      Skipping tweet collection and "
            "continuing the investigation."
        )

        return (
            [],
            "Tweet collection timed out because "
            "no twscrape account was available."
        )

    except asyncio.CancelledError:

        print(
            "\n      ⚠️ Tweet collection cancelled."
        )

        return (
            [],
            "Tweet collection was cancelled."
        )

    except Exception as exc:

        print(
            f"\n      ⚠️ Tweet collection error: "
            f"{exc}"
        )

        return (
            [],
            safe_string(exc)
        )


# =============================================================
# MAIN SCRAPER
# =============================================================

async def scrape_x_account_async(
    handle: str
) -> Dict[str, Any]:

    handle = (
        safe_string(handle)
        .replace("@", "")
        .strip()
    )

    print(
        f"      Looking up X account: "
        f"@{handle}"
    )

    # ---------------------------------------------------------
    # CREATE API
    # ---------------------------------------------------------

    api = API(
        AccountsPool()
    )

    result = {
        "status": "error",

        "profile_status": "error",

        "tweet_status": "error",

        "profile": {},

        "tweets": [],

        "requested_tweets": MAX_TWEETS,

        "tweets_collected": 0,

        "message": "",

        "tweet_error": "",
    }

    # =========================================================
    # PROFILE COLLECTION
    # =========================================================

    try:

        user = await api.user_by_login(
            handle
        )

        if user is None:

            result["status"] = "not_found"

            result["message"] = (
                "X account was not found."
            )

            return result

        profile = extract_profile(
            user
        )

        result["profile"] = profile

        result["profile_status"] = "success"

        print(
            f"      X profile found: "
            f"@{profile['username']} "
            f"({profile['display_name']})"
        )

        print_profile_summary(
            profile
        )

    except Exception as exc:

        result["message"] = (
            f"Profile lookup failed: {exc}"
        )

        print(
            f"      ❌ Profile lookup failed: "
            f"{exc}"
        )

        return result

    # =========================================================
    # TWEET COLLECTION
    # =========================================================

    tweets, tweet_error = await collect_tweets(
        api,
        user.id,
        MAX_TWEETS
    )

    result["tweets"] = tweets

    result["tweets_collected"] = len(
        tweets
    )

    result["tweet_error"] = tweet_error

    # =========================================================
    # TWEET STATUS
    # =========================================================

    if tweet_error:

        # -----------------------------------------------------
        # PARTIAL COLLECTION
        # -----------------------------------------------------

        if tweets:

            result["tweet_status"] = (
                "partial"
            )

            result["status"] = (
                "partial"
            )

            result["message"] = (
                "Profile collected and "
                f"{len(tweets)} tweets retrieved "
                "before collection stopped."
            )

            print(
                f"\n      ⚠️ Tweet collection stopped: "
                f"{tweet_error}"
            )

            print(
                f"      Preserving "
                f"{len(tweets)} tweets."
            )

        # -----------------------------------------------------
        # NO TWEETS
        # -----------------------------------------------------

        else:

            result["tweet_status"] = (
                "unavailable"
            )

            result["status"] = (
                "partial"
            )

            result["message"] = (
                "Profile collected successfully, "
                "but tweets were unavailable."
            )

            print(
                "\n      ⚠️ Tweets unavailable."
            )

            print(
                f"      Reason: {tweet_error}"
            )

            print(
                "      Continuing investigation "
                "with profile data."
            )

    # =========================================================
    # SUCCESS
    # =========================================================

    else:

        result["tweet_status"] = (
            "success"
        )

        result["status"] = (
            "success"
        )

        result["message"] = (
            "Profile and tweets collected "
            "successfully."
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    print(
        "\n      ---------- X COLLECTION ----------"
    )

    print(
        f"      Collection status: "
        f"{result['status']}"
    )

    print(
        f"      Profile status: "
        f"{result['profile_status']}"
    )

    print(
        f"      Tweet status: "
        f"{result['tweet_status']}"
    )

    print(
        f"      Tweets requested: "
        f"{MAX_TWEETS}"
    )

    print(
        f"      Tweets collected: "
        f"{len(tweets)}"
    )

    if tweet_error:

        print(
            f"      Tweet error: "
            f"{tweet_error}"
        )

    print(
        "      ----------------------------------"
    )

    return result


# =============================================================
# PUBLIC FUNCTION
# =============================================================

def scrape_x_account(
    handle: str
):

    return asyncio.run(
        scrape_x_account_async(
            handle
        )
    )


# =============================================================
# LANGGRAPH NODE
# =============================================================

def x_scraper_node(state):

    handle = state.get(
        "discovered_handle",
        ""
    )

    print(
        f"      Collecting data for: "
        f"@{handle}"
    )

    # ---------------------------------------------------------
    # NO HANDLE
    # ---------------------------------------------------------

    if not handle:

        return {
            "x_data": {
                "status": "not_found",

                "profile_status": "not_found",

                "tweet_status": "unavailable",

                "profile": {},

                "tweets": [],

                "tweets_collected": 0,

                "message": (
                    "No X handle was discovered."
                ),
            }
        }

    # ---------------------------------------------------------
    # RUN SCRAPER
    # ---------------------------------------------------------

    try:

        result = scrape_x_account(
            handle
        )

        return {
            "x_data": result
        }

    except Exception as exc:

        # Final safety net.
        #
        # The X scraper should never be able to crash
        # the entire LangGraph investigation.

        print(
            f"\n      ⚠️ X scraper error: "
            f"{exc}"
        )

        return {
            "x_data": {

                "status": "partial",

                "profile_status": "unknown",

                "tweet_status": "unavailable",

                "profile": {},

                "tweets": [],

                "tweets_collected": 0,

                "message": (
                    f"X scraper failed: {exc}"
                ),

                "tweet_error": safe_string(
                    exc
                ),
            }

        }