from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List

from Agents.BaseAgent import BaseAgent


class ActivityAnalysis(BaseModel):

    username: str
    recent_activity_summary: str
    primary_topics: List[str]
    common_hashtags: List[str]
    notable_posts: List[str]
    activity_patterns: List[str]
    confidence_level: str


class ActivityAnalyzer(BaseAgent):

    def __init__(self):
        super().__init__()

        self.activity_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an expert X/Twitter Activity Analysis Agent.

Your task is to analyze publicly available information about an
X/Twitter account's activity.

Focus only on:

- Public posts
- Topics
- Hashtags
- Recurring discussions
- Public statements
- Observable activity patterns

Do not analyze profile information such as followers,
following, bio, display name, or account type.

Rules:

1. Use ONLY the provided search results.
2. Do NOT invent tweets, posts, dates, hashtags, or activity.
3. If information is unavailable, return "Unknown".
4. Identify main topics only when supported by evidence.
5. Identify hashtags only when explicitly present.
6. Identify notable posts or statements only when supported by evidence.
7. Identify activity patterns only when sufficient evidence exists.
8. Do not infer sensitive personal attributes.
9. Do not make unsupported assumptions.
10. Keep the analysis factual and evidence-based.
11. Confidence must be High, Medium, or Low.

Return structured output only.
"""
                ),
                (
                    "human",
                    """
Analyze the public activity of the following X/Twitter account.

Username:
{username}

Search Results:
{search_results}

Extract:

1. Recent Activity Summary
2. Primary Topics
3. Common Hashtags
4. Notable Public Posts or Statements
5. Activity Patterns
6. Confidence Level

Focus ONLY on public activity.
"""
                )
            ]
        )

        self.structured_llm = self.llm.with_structured_output(
            ActivityAnalysis
        )

    def analyse_activity(self, username: str):

        activity_search = self.search(
            f'"{username}" site:x.com/{username} posts tweets'
        )

        topics_search = self.search(
            f'"{username}" X Twitter tweets topics hashtags'
        )

        notable_search = self.search(
            f'"{username}" Twitter X notable posts statements'
        )

        search_results = {
            "activity_results": activity_search,
            "topic_results": topics_search,
            "notable_results": notable_search
        }

        prompt = self.activity_prompt.invoke(
            {
                "username": username,
                "search_results": search_results
            }
        )

        return self.structured_llm.invoke(prompt)


if __name__ == "__main__":

    username = input("Enter the user name: ").strip()

    agent = ActivityAnalyzer()
    result = agent.analyse_activity(username)

    print("\n")
    print("             X ACTIVITY ANALYSIS")

    print(f"\nUsername       : @{result.username}")

    print("\nRecent Activity")
    print("-" * 60)
    print(result.recent_activity_summary)

    print("\nPrimary Topics")
    print("-" * 60)

    if result.primary_topics:
        for topic in result.primary_topics:
            print(f"• {topic}")
    else:
        print("No topics found.")

    print("\nCommon Hashtags")
    print("-" * 60)

    if result.common_hashtags:
        for hashtag in result.common_hashtags:
            print(f"• {hashtag}")
    else:
        print("No hashtags found.")

    print("\nNotable Posts / Statements")
    print("-" * 60)

    if result.notable_posts:
        for post in result.notable_posts:
            print(f"• {post}")
    else:
        print("No notable posts found.")

    print("\nActivity Patterns")
    print("-" * 60)

    if result.activity_patterns:
        for pattern in result.activity_patterns:
            print(f"• {pattern}")
    else:
        print("No activity patterns found.")

    print("\nConfidence Level")
    print("-" * 60)
    print(result.confidence_level)