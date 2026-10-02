import asyncio
import os
import re
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Tell twscrape to fail instead of waiting forever
os.environ["TWS_RAISE_WHEN_NO_ACCOUNT"] = "true"

from twscrape import API, AccountsPool


# =========================================================
# CONFIGURATION
# =========================================================

MAX_TWEETS = int(os.getenv("MAX_TWEETS", "500"))


# =========================================================
# SCRAPER
# =========================================================
def reset_twscrape_locks():
    """
    Automatically clear stale twscrape queue locks
    before starting a new investigation.
    """

    try:
        python_dir = Path(sys.executable).parent

        # Windows virtual environment
        twscrape_exe = python_dir / "twscrape.exe"

        if twscrape_exe.exists():
            command = [str(twscrape_exe), "reset_locks"]
        else:
            # Fallback if twscrape is available through PATH
            command = ["twscrape", "reset_locks"]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("      twscrape queue locks reset successfully.")
        else:
            print("      Warning: could not reset twscrape locks.")
            if result.stderr:
                print("      ", result.stderr.strip())

    except Exception as e:
        print(f"      Warning: automatic lock reset failed: {e}")

async def scrape_account(username):
    print("      Resetting twscrape queue locks...")
    reset_twscrape_locks()

    username = username.replace("@", "").strip()

    api = API(AccountsPool())

    # -----------------------------------------------------
    # Get user profile
    # -----------------------------------------------------

    try:
        user = await api.user_by_login(username)

    except Exception as e:

        return {
            "collection_status": "error",
            "profile_status": "error",
            "tweets_status": "not_collected",

            "error": str(e),

            "profile": {},
            "tweets": [],

            "tweets_requested": MAX_TWEETS,
            "tweets_collected": 0,
        }

    # -----------------------------------------------------
    # User not found
    # -----------------------------------------------------

    if not user:

        return {
            "collection_status": "not_found",
            "profile_status": "not_found",
            "tweets_status": "not_collected",

            "error": None,

            "profile": {},
            "tweets": [],

            "tweets_requested": MAX_TWEETS,
            "tweets_collected": 0,
        }

    # -----------------------------------------------------
    # Profile information
    # -----------------------------------------------------

    profile = {

        "username":
            getattr(user, "username", username),

        "display_name":
            getattr(user, "displayname", None),

        "bio":
            getattr(user, "rawDescription", None),

        "location":
            getattr(user, "location", None),

        "followers":
            getattr(user, "followersCount", None),

        "following":
            getattr(user, "followingCount", None),

        "tweets_count":
            getattr(user, "statusesCount", None),

        "verified":
            getattr(user, "verified", None),

        "created":
            str(getattr(user, "created", None)),

        "profile_url":
            f"https://x.com/{getattr(user, 'username', username)}",
    }

    # -----------------------------------------------------
    # Tweets
    # -----------------------------------------------------

    tweets = []

    seen_ids = set()

    try:

        async for tweet in api.user_tweets(
            user.id,
            limit=MAX_TWEETS
        ):

            tweet_id = getattr(tweet, "id", None)

            # Avoid duplicates
            if tweet_id in seen_ids:
                continue

            seen_ids.add(tweet_id)

            text = getattr(
                tweet,
                "rawContent",
                ""
            ) or ""

            # -------------------------------------------------
            # Mentions
            # -------------------------------------------------

            mentions = re.findall(
                r"@([A-Za-z0-9_]+)",
                text
            )

            # -------------------------------------------------
            # Hashtags
            # -------------------------------------------------

            hashtags = getattr(
                tweet,
                "hashtags",
                None
            )

            if not hashtags:

                hashtags = re.findall(
                    r"#([A-Za-z0-9_]+)",
                    text
                )

            # -------------------------------------------------
            # Store tweet
            # -------------------------------------------------

            tweets.append({

                "id": tweet_id,

                "text": text,

                "date":
                    str(getattr(
                        tweet,
                        "date",
                        None
                    )),

                "like_count":
                    getattr(
                        tweet,
                        "likeCount",
                        0
                    ),

                "retweet_count":
                    getattr(
                        tweet,
                        "retweetCount",
                        0
                    ),

                "reply_count":
                    getattr(
                        tweet,
                        "replyCount",
                        0
                    ),

                "quote_count":
                    getattr(
                        tweet,
                        "quoteCount",
                        0
                    ),

                "hashtags":
                    hashtags,

                "lang":
                    getattr(
                        tweet,
                        "lang",
                        None
                    ),

                "user_mentions":
                    mentions,

                "url":
                    (
                        f"https://x.com/"
                        f"{profile['username']}"
                        f"/status/{tweet_id}"
                        if tweet_id
                        else None
                    ),
            })

            # -------------------------------------------------
            # Stop after requested number
            # -------------------------------------------------

            if len(tweets) >= MAX_TWEETS:
                break

        # Make absolutely sure we don't exceed the limit
        tweets = tweets[:MAX_TWEETS]

        return {

            "collection_status": "success",

            "profile_status": "success",

            "tweets_status":
                "success" if tweets else "empty",

            "error": None,

            "profile": profile,

            "tweets": tweets,

            "tweets_requested": MAX_TWEETS,

            "tweets_collected": len(tweets),
        }

    except Exception as e:

        # -----------------------------------------------------
        # Partial collection
        # -----------------------------------------------------

        return {

            "collection_status": "partial",

            "profile_status": "success",

            "tweets_status": "rate_limited",

            "error": str(e),

            "profile": profile,

            "tweets": tweets,

            "tweets_requested": MAX_TWEETS,

            "tweets_collected": len(tweets),
        }


# =========================================================
# SYNC WRAPPER
# =========================================================

def scrape_x_account(username: str):

    return asyncio.run(
        scrape_account(username)
    )