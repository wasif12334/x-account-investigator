from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List

from Agents.BaseAgent import BaseAgent


class ProfileAnaylsis(BaseModel):

    username: str
    display_name: str
    bio: str
    account_type: str
    followers: int | None = None
    following: int | None = None
    post_count: int | None = None
    profile_url: str | None = None
    notable_information: List[str]
    confidence_level: str


class ProfileAnalyzer(BaseAgent):

    def __init__(self):
        super().__init__()

        self.profile_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert OSINT Profile Investigation Agent.

Your task is to analyze search results related to an X/Twitter account
and extract only information supported by the provided data.

Rules:

1. Use ONLY the provided search results.
2. Do NOT invent information.
3. If information is unavailable, return "Unknown" for text fields
   and null for numeric fields.
4. Determine the likely account type:
   Individual, Public Figure, Organization, Business, Media,
   Government, or Unknown.
5. Extract important profile information.
6. Provide concise observations based on evidence.
7. Confidence must be High, Medium, or Low.

Return structured output only.
"""
                ),
                (
                    "human",
                    """
Investigate the following X/Twitter account.

Username:
{username}

Search Results:
{search_results}

Extract:

1. Username
2. Display Name
3. Bio
4. Account Type
5. Followers
6. Following
7. Post Count
8. Profile URL
9. Important Observations
10. Confidence Level

Only use information present in the search results.
"""
                )
            ]
        )

        self.structured_llm = self.llm.with_structured_output(
            ProfileAnaylsis
        )

    def analyse_profile(self, username: str):

        profile_search = self.search(
            f'"{username}" site:x.com/{username}'
        )

        stats_search = self.search(
            f'"{username}" Twitter followers following posts'
        )

        search_results = {
            "profile_results": profile_search,
            "statistics_results": stats_search
        }

        prompt = self.profile_prompt.invoke(
            {
                "username": username,
                "search_results": search_results
            }
        )

        return self.structured_llm.invoke(prompt)


if __name__ == "__main__":

    username = input("Enter the user name: ").strip()

    agent = ProfileAnalyzer()
    result = agent.analyse_profile(username)

    print("\n")
    print("             X PROFILE ANALYSIS")

    print(f"\nUsername       : @{result.username}")
    print(f"Display Name   : {result.display_name}")
    print(f"Account Type   : {result.account_type}")

    print("\nBio")
    print("-" * 60)
    print(result.bio)

    print("\nProfile Details")
    print("-" * 60)
    print(f"Followers      : {result.followers or 'Unknown'}")
    print(f"Following      : {result.following or 'Unknown'}")
    print(f"Posts          : {result.post_count or 'Unknown'}")
    print(f"Profile URL    : {result.profile_url or 'Unknown'}")

    print("\nNotable Information")
    print("-" * 60)

    if result.notable_information:
        for information in result.notable_information:
            print(f"• {information}")
    else:
        print("No notable information found.")

    print("\nConfidence Level")
    print("-" * 60)
    print(result.confidence_level)