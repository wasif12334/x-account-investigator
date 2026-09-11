import os
from dotenv import load_dotenv

from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class BaseAgent:

    def __init__(self):

        self.search_tool = TavilySearch(
            max_results=5
        )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
        )

    def search(self, query: str):
        return self.search_tool.invoke(query)