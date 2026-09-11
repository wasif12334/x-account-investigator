from langchain_tavily import TavilySearch


search_tool = TavilySearch(
    max_results=5
)


def search_web(query: str):
    return search_tool.invoke(query)