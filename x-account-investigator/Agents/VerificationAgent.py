from Tools.llm import llm


def verification_agent(state):

    username = state.get("username", "")

    x_data = state.get("x_data", {})

    wikipedia = state.get("wikipedia_analysis", {})
    profile = state.get("profile_analysis", {})
    network = state.get("network_analysis", {})
    temporal = state.get("temporal_analysis", {})
    topics = state.get("topic_analysis", {})

    profile_data = x_data.get("profile", {})
    tweets = x_data.get("tweets", [])

    # Only summary stats
    x_summary = {
        "username": profile_data.get("username"),
        "display_name": profile_data.get("display_name"),
        "followers": profile_data.get("followers"),
        "tweets_count": profile_data.get("tweets_count"),
        "verified": profile_data.get("verified"),
        "sampled_tweets": len(tweets)
    }

    prompt = f"""
You are the evidence verification agent.

Investigation target:
@{username}

X SUMMARY:
{x_summary}

Wikipedia:
{wikipedia}

Profile Analysis:
{profile}

Network Analysis:
{network}

Temporal Analysis:
{temporal}

Topic Analysis:
{topics}

Create exactly these sections:

DIRECTLY OBSERVED

CROSS-SOURCE CONSISTENCY

NOT INDEPENDENTLY VERIFIED

DATA COLLECTION LIMITATIONS

CONFIDENCE NOTES

Rules:

- Never invent facts.
- X profile retrieval does not prove ownership.
- Wikipedia does not prove account ownership.
- Missing data means not retrieved.
- Keep concise.
- No overall confidence score.
"""

    result = llm.invoke(prompt)

    return {
        "verification_analysis": {
            "status": "success",
            "summary": result.content
        }
    }