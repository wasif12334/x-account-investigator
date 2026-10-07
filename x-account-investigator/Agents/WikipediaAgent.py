"""
Wikipedia Agent

Purpose:
    Retrieve structured identity information about the target person.

This agent should run BEFORE X account discovery.

The important principle is:
    Wikipedia provides identity evidence.
    It does NOT prove X account ownership.
"""

from typing import Any, Dict, Optional
import re

import wikipediaapi


class WikipediaAgent:
    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="XAccountInvestigator/1.0"
        )

    # ---------------------------------------------------------
    # SAFE TEXT
    # ---------------------------------------------------------

    @staticmethod
    def clean_text(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip()

    # ---------------------------------------------------------
    # EXTRACT FIRST SENTENCE
    # ---------------------------------------------------------

    @staticmethod
    def first_sentence(text: str) -> str:
        text = text.strip()

        if not text:
            return ""

        match = re.search(r"(.+?[.!?])(?:\s|$)", text)

        if match:
            return match.group(1).strip()

        return text[:500]

    # ---------------------------------------------------------
    # EXTRACT WIKIPEDIA LINKS
    # ---------------------------------------------------------

    @staticmethod
    def extract_external_links(page) -> list:
        links = []

        try:
            for url in page.links.keys():
                if url:
                    links.append(url)
        except Exception:
            pass

        return links[:50]

    # ---------------------------------------------------------
    # MAIN SEARCH
    # ---------------------------------------------------------

    def search_person(self, person_name: str) -> Dict[str, Any]:

        person_name = self.clean_text(person_name)

        print(f"\nSearching Wikipedia for: {person_name}")

        if not person_name:
            return {
                "status": "not_found",
                "query": person_name,
                "title": "",
                "summary": "",
                "confidence": 0.0,
            }

        try:

            page = self.wiki.page(person_name)

            if not page.exists():

                print("Wikipedia page not found.")

                return {
                    "status": "not_found",
                    "query": person_name,
                    "title": "",
                    "summary": "",
                    "confidence": 0.0,
                }

            title = self.clean_text(page.title)
            summary = self.clean_text(page.summary)

            exact_match = (
                title.lower().strip()
                == person_name.lower().strip()
            )

            if exact_match:
                status = "exact_match"
                confidence = 1.0
                print(f"Wikipedia exact match: {title}")
            else:
                status = "near_match"
                confidence = 0.75
                print(f"Wikipedia near match: {title}")

            return {
                "status": status,
                "query": person_name,
                "title": title,
                "summary": summary,
                "first_sentence": self.first_sentence(summary),
                "confidence": confidence,
                "url": page.fullurl,
                "links": self.extract_external_links(page),
            }

        except Exception as exc:

            print(f"Wikipedia search error: {exc}")

            return {
                "status": "search_error",
                "query": person_name,
                "title": "",
                "summary": "",
                "confidence": 0.0,
                "error": str(exc),
            }


# -------------------------------------------------------------
# LANGGRAPH NODE
# -------------------------------------------------------------

def wikipedia_agent(state):

    person_name = state.get("person_name", "").strip()

    result = WikipediaAgent().search_person(person_name)

    print("      Wikipedia analysis completed.")

    return {
        "wikipedia_data": result,
        "wikipedia_analysis": result,
    }