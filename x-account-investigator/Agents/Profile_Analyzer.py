from dotenv import load_dotenv
load_dotenv()

from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List , Optional

# OUTPUT MODEL
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

# SEARCH TOOL
SEARCH_TOOL=TavilySearch(max_result=3)

#LLM
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


#Prompt Template
profile_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert OSINT Profile Investigation Agent.

Your task is to analyze search results related to an X (Twitter) account and extract only information supported by the provided data.

Rules:
1. Use ONLY the provided search results.
2. Do NOT invent information.
3. If information is unavailable, return "Unknown".
4. Determine the likely account type:
   - Individual
   - Public Figure
   - Organization
   - Business
   - Media
   - Government
   - Unknown
5. Extract important profile information.
6. Provide concise observations based on evidence.
7. Be objective and factual.

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
3. Bio / Description
4. Account Type
5. Profile URL
6. Important Observations
7. Confidence Level (High, Medium, Low)

Only use information present in the search results.
            """
        )
    ]
)

#STRUCTURED Output initalized to the LLM

structured_llm = llm.with_structured_output(
    ProfileAnaylsis
)

# PROFILE ANALYSIS FUNCTION
def anaylse_prof(username:str):

    #Search specifically for the X/Twitter profile
    profile_search = SEARCH_TOOL.invoke(
        f'"{username}" site:x.com/{username}'
    )

    # Search for profile statistics
    stats_search = SEARCH_TOOL.invoke(
        f'"{username}" Twitter followers following posts'
    )

    search_results={
        "profile_results": profile_search,
        "statistics_results": stats_search
    }

    prompt=profile_prompt.invoke(
        {
            "username": username,
            "search_results": search_results
        }
    )

    result = structured_llm.invoke(prompt)
    print(result)
     
    # HUMAN-READABLE OUTPUT
    
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
   
# PROGRAM ENTRY POINT
if __name__ == "__main__":

    username = input("Enter the user name: ").strip()

    anaylse_prof(username)