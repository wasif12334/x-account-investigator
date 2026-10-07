"""
Verification Agent

Purpose:
    Compare:
        Wikipedia identity
        X profile
        X activity

Important:
    This agent does NOT claim ownership simply because
    the username matches the person's name.

Scores:
    1. Discovery confidence
    2. Identity consistency
    3. Ownership evidence

Ownership is deliberately conservative.
"""

import re
from typing import Dict, Any


class VerificationAgent:

    @staticmethod
    def normalize(value):

        if value is None:
            return ""

        return re.sub(
            r"[^a-z0-9 ]",
            "",
            str(value).lower()
        ).strip()

    # =========================================================
    # IDENTITY SCORE
    # =========================================================

    @classmethod
    def calculate_identity_score(
        cls,
        person_name,
        wikipedia_data,
        profile,
    ):

        score = 0
        evidence = []

        normalized_target = cls.normalize(
            person_name
        )

        display_name = cls.normalize(
            profile.get(
                "display_name",
                ""
            )
        )

        username = cls.normalize(
            profile.get(
                "username",
                ""
            )
        )

        bio = cls.normalize(
            profile.get(
                "bio",
                ""
            )
        )

        wiki_title = cls.normalize(
            wikipedia_data.get(
                "title",
                ""
            )
        )

        # -----------------------------------------------------
        # DISPLAY NAME
        # -----------------------------------------------------

        if display_name == normalized_target:

            score += 30

            evidence.append({
                "signal": "display_name_exact",
                "points": 30,
                "result": "match",
                "description": (
                    "X display name exactly matches target."
                ),
            })

        elif (
            normalized_target in display_name
            or display_name in normalized_target
        ):

            score += 20

            evidence.append({
                "signal": "display_name_partial",
                "points": 20,
                "result": "partial_match",
                "description": (
                    "X display name partially matches target."
                ),
            })

        else:

            evidence.append({
                "signal": "display_name",
                "points": 0,
                "result": "no_match",
            })

        # -----------------------------------------------------
        # USERNAME
        # -----------------------------------------------------

        compact_target = (
            normalized_target
            .replace(" ", "")
        )

        if username == compact_target:

            score += 30

            evidence.append({
                "signal": "username_exact",
                "points": 30,
                "result": "match",
                "description": (
                    "Username directly corresponds to target name."
                ),
            })

        elif compact_target in username:

            score += 20

            evidence.append({
                "signal": "username_contains_name",
                "points": 20,
                "result": "partial_match",
            })

        # -----------------------------------------------------
        # WIKIPEDIA
        # -----------------------------------------------------

        if (
            wiki_title
            and wiki_title == normalized_target
        ):

            score += 10

            evidence.append({
                "signal": "wikipedia_exact_identity",
                "points": 10,
                "result": "match",
                "description": (
                    "Wikipedia contains exact identity page."
                ),
            })

        # -----------------------------------------------------
        # BIO
        # -----------------------------------------------------

        if (
            compact_target
            and compact_target in
            bio.replace(" ", "")
        ):

            score += 10

            evidence.append({
                "signal": "bio_identity_match",
                "points": 10,
                "result": "match",
            })

        # -----------------------------------------------------
        # LOCATION
        # -----------------------------------------------------

        location = profile.get(
            "location",
            ""
        )

        if location:

            evidence.append({
                "signal": "location_available",
                "points": 0,
                "result": "observed",
                "value": location,
            })

        # -----------------------------------------------------
        # CAP
        # -----------------------------------------------------

        score = min(
            score,
            100
        )

        return score, evidence

    # =========================================================
    # OWNERSHIP EVIDENCE
    # =========================================================

    @staticmethod
    def calculate_ownership_evidence(
        profile,
        tweets,
        wikipedia_data
    ):

        evidence = []

        score = 0

        # -----------------------------------------------------
        # PROFILE ONLY
        # -----------------------------------------------------

        evidence.append({
            "signal": "profile_metadata",
            "points": 0,
            "result": "observed",
            "description": (
                "Profile metadata alone does not prove ownership."
            ),
        })

        # -----------------------------------------------------
        # VERIFIED BADGE
        # -----------------------------------------------------

        if profile.get("verified"):

            score += 20

            evidence.append({
                "signal": "verified_badge",
                "points": 20,
                "result": "present",
                "description": (
                    "Account has a verified indicator."
                ),
            })

        else:

            evidence.append({
                "signal": "verified_badge",
                "points": 0,
                "result": "not_present",
            })

        # -----------------------------------------------------
        # TWEET CONTENT
        # -----------------------------------------------------

        if tweets:

            evidence.append({
                "signal": "tweet_content",
                "points": 0,
                "result": "available",
                "description": (
                    f"{len(tweets)} tweets were collected."
                ),
            })

        else:

            evidence.append({
                "signal": "tweet_content",
                "points": 0,
                "result": "unavailable",
            })

        # -----------------------------------------------------
        # IMPORTANT:
        # DO NOT award ownership points simply because
        # tweets exist.
        # -----------------------------------------------------

        return min(
            score,
            100
        ), evidence

    # =========================================================
    # MAIN
    # =========================================================

    @classmethod
    def analyze(
        cls,
        person_name,
        wikipedia_data,
        x_data,
        discovery_confidence
    ):

        profile = x_data.get(
            "profile",
            {}
        )

        tweets = x_data.get(
            "tweets",
            []
        )

        if (
            not profile
            and not wikipedia_data
            and not tweets
        ):

            return {
                "status": "insufficient_evidence",
                "discovery_confidence": 0,
                "identity_consistency": 0,
                "ownership_evidence": 0,
                "overall_assessment": (
                    "Insufficient evidence."
                ),
                "evidence_matrix": [],
            }

        identity_score, identity_evidence = (
            cls.calculate_identity_score(
                person_name,
                wikipedia_data,
                profile,
            )
        )

        ownership_score, ownership_evidence = (
            cls.calculate_ownership_evidence(
                profile,
                tweets,
                wikipedia_data
            )
        )

        # -----------------------------------------------------
        # ASSESSMENT
        # -----------------------------------------------------

        if identity_score >= 80:

            identity_level = "strong"

        elif identity_score >= 60:

            identity_level = "moderate"

        elif identity_score >= 40:

            identity_level = "weak"

        else:

            identity_level = "very_weak"

        if ownership_score >= 70:

            ownership_level = "strong"

        elif ownership_score >= 40:

            ownership_level = "moderate"

        else:

            ownership_level = "insufficient"

        evidence_matrix = (
            identity_evidence
            + ownership_evidence
        )

        return {
            "status": "analyzed",

            "discovery_confidence": (
                discovery_confidence
            ),

            "identity_consistency": (
                identity_score
            ),

            "identity_level": (
                identity_level
            ),

            "ownership_evidence": (
                ownership_score
            ),

            "ownership_level": (
                ownership_level
            ),

            "evidence_matrix": (
                evidence_matrix
            ),

            "overall_assessment": (
                "Strong identity consistency, "
                "but ownership cannot be established "
                "without independent corroboration."
                if identity_score >= 80
                else
                "Evidence is insufficient to "
                "establish a strong identity match."
            ),
        }


def verification_agent(state):

    print(
        "      Verification completed."
    )

    person_name = state.get(
        "person_name",
        ""
    )

    wikipedia_data = state.get(
        "wikipedia_data",
        {}
    )

    x_data = state.get(
        "x_data",
        {}
    )

    discovery_confidence = state.get(
        "discovery_confidence",
        0
    )

    result = VerificationAgent.analyze(
        person_name,
        wikipedia_data,
        x_data,
        discovery_confidence
    )

    return {
        "verification_analysis": result
    }