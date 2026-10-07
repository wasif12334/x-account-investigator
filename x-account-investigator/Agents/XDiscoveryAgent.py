"""
X Account Discovery Agent

Purpose:
    Discover likely X accounts for a person.

Important architecture rule:

    Discovery = candidate generation + ranking

    Verification = identity decision

Discovery should NEVER throw away the best candidate simply
because its score is below the confidence threshold.
"""

import asyncio
import re
from typing import Any, Dict, List

from twscrape import API, AccountsPool


class XDiscoveryAgent:

    SEARCH_LIMIT = 20

    def __init__(self):
        self.api = API(AccountsPool())

    # =========================================================
    # NORMALIZATION
    # =========================================================

    @staticmethod
    def normalize(value: Any) -> str:

        if value is None:
            return ""

        value = str(value).lower().strip()

        value = re.sub(
            r"[^a-z0-9 ]",
            " ",
            value
        )

        value = re.sub(
            r"\s+",
            " ",
            value
        )

        return value.strip()

    # =========================================================
    # HANDLE NORMALIZATION
    # =========================================================

    @staticmethod
    def normalize_handle(handle: str) -> str:

        return (
            str(handle)
            .replace("@", "")
            .strip()
            .lower()
        )

    # =========================================================
    # SAFE USER FIELD
    # =========================================================

    @staticmethod
    def get_user_field(
        user,
        *names,
        default=None
    ):

        for name in names:

            try:

                value = getattr(
                    user,
                    name
                )

                if value is not None:
                    return value

            except Exception:
                pass

        return default

    # =========================================================
    # GENERATE HANDLE CANDIDATES
    # =========================================================

    def generate_handles(
        self,
        person_name: str
    ) -> List[str]:

        parts = [
            p.lower()
            for p in person_name.split()
            if p.strip()
        ]

        if not parts:
            return []

        first = parts[0]
        last = parts[-1]

        candidates = [
            f"{first}{last}",
            f"{first}_{last}",
            f"{first}.{last}",
            f"{first}{last[0]}",
            f"{first[0]}{last}",
            f"{last}{first}",
            f"{last}_{first}",
        ]

        return list(
            dict.fromkeys(candidates)
        )

    # =========================================================
    # EXTRACT WIKIPEDIA CONTEXT
    # =========================================================

    def extract_wikipedia_terms(
        self,
        wikipedia_data: Dict[str, Any]
    ):

        summary = self.normalize(
            wikipedia_data.get(
                "summary",
                ""
            )
        )

        title = self.normalize(
            wikipedia_data.get(
                "title",
                ""
            )
        )

        combined = (
            f"{title} {summary}"
        )

        # Important identity terms.
        identity_terms = set()

        important_terms = {
            "founder",
            "chairman",
            "ceo",
            "chief",
            "executive",
            "businessman",
            "businesswoman",
            "investor",
            "entrepreneur",
            "technology",
            "technologies",
            "company",
            "president",
            "owner",
            "philanthropist",
            "billionaire",
            "manager",
            "director",
        }

        words = set(
            re.findall(
                r"\b[a-z]{4,}\b",
                combined
            )
        )

        identity_terms.update(
            words.intersection(
                important_terms
            )
        )

        # Known organization phrases from summary.
        organization_patterns = [
            r"dell technologies",
            r"dell inc",
            r"df[o0] management",
            r"las vegas raiders",
        ]

        organizations = []

        for pattern in organization_patterns:

            match = re.search(
                pattern,
                summary
            )

            if match:

                organizations.append(
                    match.group(0)
                )

        return {
            "terms": identity_terms,
            "organizations": organizations,
            "summary": summary,
        }

    # =========================================================
    # SCORE CANDIDATE
    # =========================================================

    def score_candidate(
        self,
        person_name: str,
        user,
        wikipedia_data: Dict[str, Any],
        source: str = "unknown"
    ) -> Dict[str, Any]:

        score = 0

        evidence = []

        # -----------------------------------------------------
        # PROFILE DATA
        # -----------------------------------------------------

        username = self.get_user_field(
            user,
            "username",
            default=""
        )

        display_name = self.get_user_field(
            user,
            "displayname",
            "display_name",
            default=""
        )

        bio = self.get_user_field(
            user,
            "rawDescription",
            "description",
            default=""
        )

        location = self.get_user_field(
            user,
            "location",
            default=""
        )

        username = str(username or "")
        display_name = str(
            display_name or ""
        )
        bio = str(bio or "")
        location = str(location or "")

        # -----------------------------------------------------
        # NORMALIZED
        # -----------------------------------------------------

        target = self.normalize(
            person_name
        )

        target_compact = (
            target.replace(" ", "")
        )

        normalized_username = self.normalize(
            username
        ).replace(" ", "")

        normalized_display = self.normalize(
            display_name
        )

        normalized_bio = self.normalize(
            bio
        )

        normalized_location = self.normalize(
            location
        )

        # -----------------------------------------------------
        # WIKIPEDIA
        # -----------------------------------------------------

        wiki_context = (
            self.extract_wikipedia_terms(
                wikipedia_data
            )
        )

        # -----------------------------------------------------
        # 1. EXACT DISPLAY NAME
        # -----------------------------------------------------

        if normalized_display == target:

            score += 30

            evidence.append({
                "signal": "exact_display_name",
                "points": 30,
                "description": (
                    "X display name exactly matches "
                    "the investigation target."
                )
            })

        elif (
            target in normalized_display
            or normalized_display in target
        ):

            score += 20

            evidence.append({
                "signal": "partial_display_name",
                "points": 20,
                "description": (
                    "X display name partially matches "
                    "the investigation target."
                )
            })

        # -----------------------------------------------------
        # 2. USERNAME
        # -----------------------------------------------------

        if normalized_username == target_compact:

            score += 25

            evidence.append({
                "signal": "exact_username",
                "points": 25,
                "description": (
                    "X username directly corresponds "
                    "to the target's name."
                )
            })

        elif target_compact in normalized_username:

            score += 15

            evidence.append({
                "signal": "username_contains_name",
                "points": 15,
                "description": (
                    "X username contains the target name."
                )
            })

        # -----------------------------------------------------
        # 3. WIKIPEDIA TITLE
        # -----------------------------------------------------

        wiki_title = self.normalize(
            wikipedia_data.get(
                "title",
                ""
            )
        )

        if (
            wiki_title
            and normalized_display == wiki_title
        ):

            score += 10

            evidence.append({
                "signal": "wikipedia_name_match",
                "points": 10,
                "description": (
                    "X display name matches the "
                    "Wikipedia identity."
                )
            })

        # -----------------------------------------------------
        # 4. ORGANIZATION MATCH
        # -----------------------------------------------------

        matched_orgs = []

        for organization in (
            wiki_context["organizations"]
        ):

            org_normalized = self.normalize(
                organization
            )

            if (
                org_normalized
                and org_normalized
                in normalized_bio
            ):

                matched_orgs.append(
                    organization
                )

        if matched_orgs:

            score += min(
                20,
                len(matched_orgs) * 10
            )

            evidence.append({
                "signal": "organization_match",
                "points": min(
                    20,
                    len(matched_orgs) * 10
                ),
                "description": (
                    "Organization associated with "
                    "the Wikipedia identity appears "
                    "in the X profile."
                ),
                "organizations": matched_orgs,
            })

        # -----------------------------------------------------
        # 5. OCCUPATION MATCH
        # -----------------------------------------------------

        occupation_matches = []

        for term in wiki_context["terms"]:

            if term in normalized_bio:

                occupation_matches.append(
                    term
                )

        if occupation_matches:

            score += min(
                10,
                len(occupation_matches) * 3
            )

            evidence.append({
                "signal": "occupation_context",
                "points": min(
                    10,
                    len(occupation_matches) * 3
                ),
                "description": (
                    "Professional identity terms "
                    "overlap between Wikipedia and X bio."
                ),
                "matched_terms": (
                    occupation_matches[:10]
                ),
            })

        # -----------------------------------------------------
        # 6. LOCATION
        # -----------------------------------------------------

        if normalized_location:

            evidence.append({
                "signal": "profile_location",
                "points": 0,
                "description": (
                    "X profile contains a location."
                ),
                "location": location,
            })

        # -----------------------------------------------------
        # 7. SOURCE
        # -----------------------------------------------------

        if source == "x_search":

            score += 5

            evidence.append({
                "signal": "x_search_candidate",
                "points": 5,
                "description": (
                    "Candidate was returned by X user search."
                )
            })

        # -----------------------------------------------------
        # CAP
        # -----------------------------------------------------

        score = min(
            score,
            100
        )

        return {
            "handle": username,
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "location": location,
            "score": score,
            "source": source,
            "evidence": evidence,
        }

    # =========================================================
    # SEARCH X
    # =========================================================

    async def search_x_users(
        self,
        person_name: str
    ):

        users = []

        try:

            print(
                f"      X user search: "
                f"{person_name}"
            )

            async for user in self.api.search_user(
                person_name,
                limit=self.SEARCH_LIMIT
            ):

                users.append(user)

            print(
                f"      X search candidates: "
                f"{len(users)}"
            )

        except Exception as exc:

            print(
                f"      X search failed: "
                f"{exc}"
            )

        return users

    # =========================================================
    # DISCOVER
    # =========================================================

    async def discover_async(
        self,
        person_name: str,
        wikipedia_data: Dict[str, Any]
    ):

        print(
            f"      Discovering X account for: "
            f"{person_name}"
        )

        candidate_map = {}

        # -----------------------------------------------------
        # GENERATED HANDLES
        # -----------------------------------------------------

        generated_handles = (
            self.generate_handles(
                person_name
            )
        )

        print(
            f"      Generated handle candidates: "
            f"{len(generated_handles)}"
        )

        for handle in generated_handles:

            clean = self.normalize_handle(
                handle
            )

            candidate_map[
                clean
            ] = {
                "handle": clean,
                "source": "generated"
            }

        # -----------------------------------------------------
        # X SEARCH
        # -----------------------------------------------------

        x_users = await self.search_x_users(
            person_name
        )

        for user in x_users:

            username = self.get_user_field(
                user,
                "username",
                default=""
            )

            username = self.normalize_handle(
                str(username or "")
            )

            if username:

                # Keep the actual user object.
                candidate_map[
                    username
                ] = {
                    "handle": username,
                    "source": "x_search",
                    "user": user,
                }

        print(
            f"      Total candidates: "
            f"{len(candidate_map)}"
        )

        # -----------------------------------------------------
        # VALIDATE / SCORE
        # -----------------------------------------------------

        scored = []

        for handle, candidate in (
            candidate_map.items()
        ):

            print(
                f"      Checking @{handle}..."
            )

            user = candidate.get(
                "user"
            )

            # If this came from generated handles,
            # look it up directly.
            if user is None:

                try:

                    user = await self.api.user_by_login(
                        handle
                    )

                except Exception as exc:

                    print(
                        f"         lookup failed: "
                        f"{exc}"
                    )

                    continue

            if user is None:
                continue

            result = self.score_candidate(
                person_name,
                user,
                wikipedia_data,
                candidate["source"]
            )

            scored.append(
                result
            )

        # -----------------------------------------------------
        # SORT DETERMINISTICALLY
        # -----------------------------------------------------

        scored.sort(
            key=lambda item: (
                -item["score"],
                item["username"].lower()
            )
        )

        # -----------------------------------------------------
        # NO CANDIDATE
        # -----------------------------------------------------

        if not scored:

            print(
                "      No usable X candidates found."
            )

            return {
                "status": "not_found",
                "discovered_handle": "",
                "confidence": 0,
                "best_candidate": None,
                "candidates": [],
            }

        # -----------------------------------------------------
        # BEST
        # -----------------------------------------------------

        best = scored[0]

        second_score = (
            scored[1]["score"]
            if len(scored) > 1
            else 0
        )

        margin = (
            best["score"]
            - second_score
        )

        # -----------------------------------------------------
        # CLASSIFICATION
        # -----------------------------------------------------

        if best["score"] >= 75 and margin >= 10:

            status = "confident"

        elif best["score"] >= 50:

            status = "likely"

        else:

            status = "uncertain"

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # ALWAYS KEEP BEST HANDLE.
        #
        # Verification decides whether it is correct.
        # -----------------------------------------------------

        discovered_handle = best[
            "username"
        ]

        print(
            f"      Best candidate: "
            f"@{discovered_handle}"
        )

        print(
            f"      Confidence: "
            f"{best['score']}/100"
        )

        print(
            f"      Margin over second: "
            f"{margin}"
        )

        print(
            f"      Discovery status: "
            f"{status.upper()}"
        )

        return {
            "status": status,

            "discovered_handle": (
                discovered_handle
            ),

            "confidence": (
                best["score"]
            ),

            "margin": margin,

            "best_candidate": best,

            "candidates": scored,
        }

    # =========================================================
    # SYNC
    # =========================================================

    def discover(
        self,
        person_name: str,
        wikipedia_data: Dict[str, Any]
    ):

        return asyncio.run(
            self.discover_async(
                person_name,
                wikipedia_data
            )
        )


# =============================================================
# LANGGRAPH NODE
# =============================================================

def x_discovery_agent(state):

    person_name = state.get(
        "person_name",
        ""
    )

    wikipedia_data = state.get(
        "wikipedia_data",
        {}
    )

    agent = XDiscoveryAgent()

    result = agent.discover(
        person_name,
        wikipedia_data
    )

    handle = result.get(
        "discovered_handle",
        ""
    )

    return {
        "x_candidates": result.get(
            "candidates",
            []
        ),

        "discovered_handle": handle,

        "username": handle,

        "discovery_confidence": result.get(
            "confidence",
            0
        ),

        "discovery_evidence": result,
    }