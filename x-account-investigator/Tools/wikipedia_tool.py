import re
import requests
import wikipediaapi
from difflib import SequenceMatcher


WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


wiki = wikipediaapi.Wikipedia(
    user_agent="XAccountInvestigator/1.0",
    language="en"
)


def clean_query(query: str) -> str:
    """
    Keep the original words/spaces.

    Example:
        '@elon mask' -> 'elon mask'
        'elonmask'   -> 'elonmask'
    """

    if query is None:
        return ""

    query = str(query)
    query = query.replace("@", "")
    query = " ".join(query.split())

    return query.strip()


def normalize_name(value: str) -> str:

    if not value:
        return ""

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]",
        "",
        value
    )

    return value


def similarity(a: str, b: str) -> float:

    a = normalize_name(a)
    b = normalize_name(b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


def wikipedia_search(query: str):

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": 10,
    }

    response = requests.get(
        WIKIPEDIA_API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def wikipedia_lookup(query: str):

    query = clean_query(query)

    if not query:

        return {
            "status": "invalid",
            "found": False,
            "possible_match": False,
            "title": None,
            "summary": None,
            "url": None,
            "candidates": [],
            "error": "Empty Wikipedia query."
        }

    # ==================================================
    # STEP 1 — EXACT PAGE
    # ==================================================

    try:

        page = wiki.page(query)

        if page.exists():

            return {
                "status": "exact",
                "found": True,
                "possible_match": False,
                "title": page.title,
                "summary": page.summary,
                "url": page.fullurl,
                "candidates": [],
                "error": None
            }

    except Exception as e:

        print(
            f"Wikipedia exact lookup error: {e}"
        )

    # ==================================================
    # STEP 2 — SEARCH API
    # ==================================================

    try:

        data = wikipedia_search(query)

        results = (
            data
            .get("query", {})
            .get("search", [])
        )

        candidates = []

        for result in results:

            title = result.get(
                "title",
                ""
            ).strip()

            if not title:
                continue

            try:

                page = wiki.page(title)

                if not page.exists():
                    continue

                score = similarity(
                    query,
                    title
                )

                candidates.append({

                    "title": page.title,

                    "summary": page.summary,

                    "url": page.fullurl,

                    "snippet": result.get(
                        "snippet",
                        ""
                    ),

                    "similarity": round(
                        score * 100,
                        2
                    )

                })

            except Exception:
                continue

        # Highest similarity first
        candidates.sort(
            key=lambda item:
            item.get(
                "similarity",
                0
            ),
            reverse=True
        )

        if candidates:

            best = candidates[0]

            print(
                "Wikipedia possible match:",
                best["title"]
            )

            return {

                "status": "near_match",

                "found": False,

                "possible_match": True,

                "title": best["title"],

                "summary": best["summary"],

                "url": best["url"],

                "candidates": candidates[:5],

                "error": None

            }

        return {

            "status": "not_found",

            "found": False,

            "possible_match": False,

            "title": None,

            "summary": None,

            "url": None,

            "candidates": [],

            "error": None

        }

    except Exception as e:

        return {

            "status": "search_error",

            "found": False,

            "possible_match": False,

            "title": None,

            "summary": None,

            "url": None,

            "candidates": [],

            "error": str(e)

        }