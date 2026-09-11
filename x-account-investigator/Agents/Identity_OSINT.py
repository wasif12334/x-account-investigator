from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List

from Agents.BaseAgent import BaseAgent


class IdentityOSINTAnalysis(BaseModel):

    username: str
    identified_entity: str
    professional_background: List[str]
    public_websites: List[str]
    professional_profiles: List[str]
    organizations: List[str]
    public_affiliations: List[str]
    possible_identity_matches: List[str]
    supporting_evidence: List[str]
    confidence_level: str


class IdentityOSINTAgent(BaseAgent):

    def __init__(self):
        super().__init__()

        self.osint_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert Identity and OSINT Investigation Agent.

Your task is to investigate the publicly documented web presence
associated with an X/Twitter account.

Your focus is information OUTSIDE the X/Twitter profile itself.

Investigate:

- Public professional background
- Official websites
- Public professional profiles
- Organizations and companies
- Public affiliations
- Publicly documented biography
- Possible identity matches across public sources
- Supporting evidence

Do not repeat X profile information unless it is necessary
to establish or verify an identity connection.

Rules:

1. Use ONLY the provided search results.
2. Do NOT invent information.
3. Do NOT assume that two profiles belong to the same person
   without supporting evidence.
4. Clearly distinguish confirmed information from possible matches.
5. Only include publicly available information.
6. Do not infer sensitive personal attributes.
7. Do not make unsupported assumptions.
8. Do not identify private individuals from weak evidence.
9. Include supporting evidence for important findings.
10. Confidence must be High, Medium, or Low.
11. If information is unavailable, use "Unknown" for text fields
    and an empty list for list fields.

Return structured output only.
"""
                ),
                (
                    "human",
                    """
Investigate the public web presence associated with this
X/Twitter account.

Username:
{username}

Search Results:
{search_results}

Extract:

1. Identified Entity
2. Professional Background
3. Public Websites
4. Professional Profiles
5. Organizations
6. Public Affiliations
7. Possible Identity Matches
8. Supporting Evidence
9. Confidence Level

Focus on information outside X/Twitter.

Only use information supported by the provided search results.
"""
                )
            ]
        )

        self.structured_llm = self.llm.with_structured_output(
            IdentityOSINTAnalysis
        )

    def analyse_identity(self, username: str):

        background_search = self.search(
            f'"{username}" biography professional background'
        )

        website_search = self.search(
            f'"{username}" official website'
        )

        professional_search = self.search(
            f'"{username}" LinkedIn professional profile'
        )

        organizations_search = self.search(
            f'"{username}" company organization affiliation'
        )

        identity_search = self.search(
            f'"{username}" "official" biography profile'
        )

        search_results = {
            "background_results": background_search,
            "website_results": website_search,
            "professional_results": professional_search,
            "organizations_results": organizations_search,
            "identity_results": identity_search
        }

        prompt = self.osint_prompt.invoke(
            {
                "username": username,
                "search_results": search_results
            }
        )

        return self.structured_llm.invoke(prompt)


if __name__ == "__main__":

    username = input("Enter the user name: ").strip()

    agent = IdentityOSINTAgent()
    result = agent.analyse_identity(username)

    print("\n")
    print("             X IDENTITY & OSINT ANALYSIS")

    print(f"\nUsername       : @{result.username}")
    print(f"Identified Entity : {result.identified_entity}")

    print("\nProfessional Background")
    print("-" * 60)

    if result.professional_background:
        for item in result.professional_background:
            print(f"• {item}")
    else:
        print("No professional background found.")

    print("\nPublic Websites")
    print("-" * 60)

    if result.public_websites:
        for website in result.public_websites:
            print(f"• {website}")
    else:
        print("No public websites found.")

    print("\nProfessional Profiles")
    print("-" * 60)

    if result.professional_profiles:
        for profile in result.professional_profiles:
            print(f"• {profile}")
    else:
        print("No professional profiles found.")

    print("\nOrganizations")
    print("-" * 60)

    if result.organizations:
        for organization in result.organizations:
            print(f"• {organization}")
    else:
        print("No organizations found.")

    print("\nPublic Affiliations")
    print("-" * 60)

    if result.public_affiliations:
        for affiliation in result.public_affiliations:
            print(f"• {affiliation}")
    else:
        print("No public affiliations found.")

    print("\nPossible Identity Matches")
    print("-" * 60)

    if result.possible_identity_matches:
        for match in result.possible_identity_matches:
            print(f"• {match}")
    else:
        print("No possible identity matches found.")

    print("\nSupporting Evidence")
    print("-" * 60)

    if result.supporting_evidence:
        for evidence in result.supporting_evidence:
            print(f"• {evidence}")
    else:
        print("No supporting evidence found.")

    print("\nConfidence Level")
    print("-" * 60)
    print(result.confidence_level)