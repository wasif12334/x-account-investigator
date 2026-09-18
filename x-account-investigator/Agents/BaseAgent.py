from dotenv import load_dotenv
load_dotenv()

from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI


class BaseAgent:

    def __init__(self):
        self.search_tool = TavilySearch(
            max_results=5
        )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash"
        )

    def search(self, query: str):
        return self.search_tool.invoke(query)