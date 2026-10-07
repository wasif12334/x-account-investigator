from langgraph.graph import StateGraph, START, END

from graph.state import InvestigatorState

from Agents.WikipediaAgent import wikipedia_agent
from Agents.XDiscoveryAgent import x_discovery_agent
from Tools.x_scraper_tool import x_scraper_node

from Agents.Profile_Analyzer import profile_agent
from Agents.NetworkAgent import network_agent
from Agents.TemporalAgent import temporal_agent
from Agents.TopicAgent import topic_agent
from Agents.VerificationAgent import verification_agent
from Agents.ReportAgent import report_agent


def build_graph():

    workflow = StateGraph(
        InvestigatorState
    )

    workflow.add_node(
        "wikipedia",
        wikipedia_agent
    )

    workflow.add_node(
        "x_discovery",
        x_discovery_agent
    )

    workflow.add_node(
        "x_scraper",
        x_scraper_node
    )

    workflow.add_node(
        "profile",
        profile_agent
    )

    workflow.add_node(
        "network",
        network_agent
    )

    workflow.add_node(
        "temporal",
        temporal_agent
    )

    workflow.add_node(
        "topic",
        topic_agent
    )

    workflow.add_node(
        "verification",
        verification_agent
    )

    workflow.add_node(
        "report",
        report_agent
    )

    workflow.add_edge(
        START,
        "wikipedia"
    )

    workflow.add_edge(
        "wikipedia",
        "x_discovery"
    )

    workflow.add_edge(
        "x_discovery",
        "x_scraper"
    )

    workflow.add_edge(
        "x_scraper",
        "profile"
    )

    workflow.add_edge(
        "profile",
        "network"
    )

    workflow.add_edge(
        "network",
        "temporal"
    )

    workflow.add_edge(
        "temporal",
        "topic"
    )

    workflow.add_edge(
        "topic",
        "verification"
    )

    workflow.add_edge(
        "verification",
        "report"
    )

    workflow.add_edge(
        "report",
        END
    )

    return workflow.compile()