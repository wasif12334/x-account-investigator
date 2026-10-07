"""
Profile Analysis Agent

Pure deterministic analysis of X profile metadata.
"""

import re


class ProfileAgent:

    @staticmethod
    def normalize(value):

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def analyze(profile):

        if not profile:

            return {
                "status": "not_analyzed",
                "summary": "No X profile data available.",
            }

        username = ProfileAgent.normalize(
            profile.get("username")
        )

        display_name = ProfileAgent.normalize(
            profile.get("display_name")
        )

        bio = ProfileAgent.normalize(
            profile.get("bio")
        )

        location = ProfileAgent.normalize(
            profile.get("location")
        )

        followers = profile.get(
            "followers",
            0
        )

        following = profile.get(
            "following",
            0
        )

        tweets_count = profile.get(
            "tweets_count",
            0
        )

        verified = profile.get(
            "verified",
            False
        )

        bio_words = re.findall(
            r"\b[A-Za-z]{3,}\b",
            bio
        )

        return {
            "status": "analyzed",
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "location": location,
            "followers": followers,
            "following": following,
            "tweets_count": tweets_count,
            "verified": verified,
            "bio_word_count": len(bio_words),
            "profile_url": profile.get(
                "profile_url",
                ""
            ),
        }


def profile_agent(state):

    x_data = state.get(
        "x_data",
        {}
    )

    profile = x_data.get(
        "profile",
        {}
    )

    result = ProfileAgent.analyze(
        profile
    )

    print(
        "      Profile analysis completed."
    )

    return {
        "profile_analysis": result
    }