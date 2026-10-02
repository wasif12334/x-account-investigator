from Tools.wikipedia_tool import wikipedia_lookup
from Tools.llm import llm


def wikipedia_agent(state):

    username = state["username"]

    wiki_data = wikipedia_lookup(
        username
    )

    # -----------------------------------------------------
    # No Wikipedia result
    # -----------------------------------------------------

    if not wiki_data["found"]:

        return {

            "wikipedia_data":
                wiki_data,

            "wikipedia_analysis": {

                "status":
                    wiki_data["status"],

                "summary":
                    (
                        f"No matching Wikipedia page "
                        f"was retrieved for the exact "
                        f"query '{username}'."
                    ),
            },
        }

    # -----------------------------------------------------
    # Analyze Wikipedia
    # -----------------------------------------------------

    prompt = f"""
You are the Wikipedia background research agent
in an X-account investigation system.

Target:
@{username}

Wikipedia source:
{wiki_data}

Extract ONLY concise identity-relevant information.

Return exactly:

Entity / Full Name:
Entity Type:
Description:
Country / Nationality:
Occupation / Role:
Known For:
Relevant Affiliations:
Relevant Identifying Facts:
Source URL:

Rules:

1. Use ONLY the supplied Wikipedia source.

2. Do not add information from memory.

3. Do not include unnecessary:
   - budgets
   - employee numbers
   - long history
   - unrelated partners
   - trivia

4. Keep the response concise.

5. If information is unavailable,
   write "Not available."

6. A Wikipedia page does NOT prove that
   the X account belongs to the same person
   or organization.

7. Do not make identity claims.
"""

    result = llm.invoke(
        prompt
    )

    return {

        "wikipedia_data":
            wiki_data,

        "wikipedia_analysis": {

            "status": "success",

            "summary":
                result.content,
        },
    }