from graph.state import InvestigatorState
from Agents.WikipediaAgent import wikipedia_agent
from Agents.Profile_Analyzer import profile_agent
from Agents.NetworkAgent import network_agent
from Agents.TemporalAgent import temporal_agent
from Agents.TopicAgent import topic_agent
from Agents.VerificationAgent import verification_agent
from Agents.ReportAgent import report_agent
from langgraph.graph import StateGraph, START, END
from graph.state import InvestigatorState
from Tools.x_scraper_tool import scrape_x_account



# =========================================================
# WIKIPEDIA NODE
# =========================================================

def wikipedia_node(state: InvestigatorState):

    username = state.get("username", "").strip()

    print("\n[1/8] Wikipedia Agent")
    print(f"      Searching Wikipedia for: {username}")

    result = wikipedia_agent(state)

    print("      Wikipedia analysis completed.")

    return result


# =========================================================
# X SCRAPER NODE
# =========================================================

def x_scraper_node(state: InvestigatorState):

    username = state.get("username", "").strip()

    print("\n[2/8] X Scraper")
    print(f"      Collecting data for: @{username}")

    x_data = scrape_x_account(username)

    # -----------------------------------------------------
    # DEBUG INFORMATION
    # -----------------------------------------------------

    print("\n      ---------- X COLLECTION ----------")

    print(
        "      Collection status:",
        x_data.get("collection_status")
    )

    print(
        "      Profile status:",
        x_data.get("profile_status")
    )

    print(
        "      Tweet status:",
        x_data.get("tweets_status")
    )

    print(
        "      Tweets requested:",
        x_data.get("tweets_requested")
    )

    print(
        "      Tweets collected:",
        x_data.get("tweets_collected")
    )

    if x_data.get("error"):
        print(
            "      Collection message:",
            x_data.get("error")
        )

    print("      ----------------------------------")

    # -----------------------------------------------------
    # IMPORTANT
    #
    # Store the COMPLETE scraper result under x_data.
    #
    # Downstream agents should access:
    #
    # state["x_data"]["profile"]
    # state["x_data"]["tweets"]
    # -----------------------------------------------------

    return {
        "x_data": x_data
    }


# =========================================================
# PROFILE NODE
# =========================================================

def profile_node(state: InvestigatorState):

    print("\n[3/8] Profile Agent")

    result = profile_agent(state)

    print("      Profile analysis completed.")

    return result


# =========================================================
# NETWORK NODE
# =========================================================

def network_node(state: InvestigatorState):

    tweets = (
        state
        .get("x_data", {})
        .get("tweets", [])
    )

    print("\n[4/8] Network / Mention Agent")
    print(
        f"      Tweets received by agent: {len(tweets)}"
    )

    result = network_agent(state)

    print("      Network analysis completed.")

    return result


# =========================================================
# TEMPORAL NODE
# =========================================================

def temporal_node(state: InvestigatorState):

    tweets = (
        state
        .get("x_data", {})
        .get("tweets", [])
    )

    print("\n[5/8] Temporal Agent")
    print(
        f"      Tweets received by agent: {len(tweets)}"
    )

    result = temporal_agent(state)

    print("      Temporal analysis completed.")

    return result


# =========================================================
# TOPIC NODE
# =========================================================

def topic_node(state: InvestigatorState):

    tweets = (
        state
        .get("x_data", {})
        .get("tweets", [])
    )

    print("\n[6/8] Topic Agent")
    print(
        f"      Tweets received by agent: {len(tweets)}"
    )

    result = topic_agent(state)

    print("      Topic analysis completed.")

    return result


# =========================================================
# VERIFICATION NODE
# =========================================================

def verification_node(state: InvestigatorState):

    print("\n[7/8] Verification Agent")

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # VerificationAgent should NOT receive raw tweets
    # in its LLM prompt.
    #
    # It receives the complete LangGraph state here,
    # but the updated VerificationAgent only uses:
    #
    # - profile summary
    # - Wikipedia analysis
    # - network analysis
    # - temporal analysis
    # - topic analysis
    #
    # This prevents the previous 92,491-token error.
    # -----------------------------------------------------

    result = verification_agent(state)

    print("      Verification completed.")

    return result


# =========================================================
# REPORT NODE
# =========================================================

def report_node(state: InvestigatorState):

    print("\n[8/8] Report Agent")

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # ReportAgent should use the analysis results rather
    # than sending the complete raw tweet dataset to Groq.
    # -----------------------------------------------------

    result = report_agent(state)

    print("      Final report generated.")

    return result


# =========================================================
# BUILD LANGGRAPH
# =========================================================

def build_investigator_graph():

    workflow = StateGraph(InvestigatorState)

    # -----------------------------------------------------
    # ADD NODES
    # -----------------------------------------------------

    workflow.add_node(
        "wikipedia",
        wikipedia_node
    )

    workflow.add_node(
        "x_scraper",
        x_scraper_node
    )

    workflow.add_node(
        "profile",
        profile_node
    )

    workflow.add_node(
        "network",
        network_node
    )

    workflow.add_node(
        "temporal",
        temporal_node
    )

    workflow.add_node(
        "topic",
        topic_node
    )

    workflow.add_node(
        "verification",
        verification_node
    )

    workflow.add_node(
        "report",
        report_node
    )

    # -----------------------------------------------------
    # GRAPH FLOW
    # -----------------------------------------------------

    workflow.add_edge(
        START,
        "wikipedia"
    )

    workflow.add_edge(
        "wikipedia",
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

    # -----------------------------------------------------
    # COMPILE
    # -----------------------------------------------------

    return workflow.compile()


# =========================================================
# GRAPH INSTANCE
# =========================================================

graph = build_investigator_graph()