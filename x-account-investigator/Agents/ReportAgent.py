from Tools.llm import llm
from reports.pdf_generator import ReportGenerator


def report_agent(state):

    username = state.get(
        "username",
        ""
    )

    x_data = state.get(
        "x_data",
        {}
    )

    wikipedia = state.get(
        "wikipedia_analysis",
        {}
    )

    profile = state.get(
        "profile_analysis",
        {}
    )

    network = state.get(
        "network_analysis",
        {}
    )

    temporal = state.get(
        "temporal_analysis",
        {}
    )

    topics = state.get(
        "topic_analysis",
        {}
    )

    verification = state.get(
        "verification_analysis",
        {}
    )

    # -----------------------------------------------------
    # REPORT PROMPT
    # -----------------------------------------------------

    prompt = f"""

Create a professional factual investigation report.

Target:
@{username}

==================================================
X COLLECTION
==================================================

Collection status:
{x_data.get("collection_status", "unknown")}

Profile status:
{x_data.get("profile_status", "unknown")}

Tweet status:
{x_data.get("tweets_status", "unknown")}

Tweets requested:
{x_data.get("tweets_requested", "unknown")}

Tweets collected:
{x_data.get("tweets_collected", 0)}


==================================================
WIKIPEDIA
==================================================

{wikipedia}


==================================================
X PROFILE
==================================================

{profile}


==================================================
MENTION ANALYSIS
==================================================

{network}


==================================================
TEMPORAL ANALYSIS
==================================================

{temporal}


==================================================
TOPICS
==================================================

{topics}


==================================================
VERIFICATION
==================================================

{verification}


==================================================
REPORT STRUCTURE
==================================================

Use exactly these sections:

1. Executive Summary

2. Subject Identification

3. X Profile

4. Mention Analysis

5. Temporal Activity

6. Topics & Interests

7. Wikipedia Background

8. Verification & Evidence

9. Data Collection Limitations


==================================================
REPORTING RULES
==================================================

1. Use ONLY the supplied evidence.

2. Never invent facts.

3. Do not repeat the same information unnecessarily.

4. Executive Summary must be short.

5. Subject Identification must distinguish:

   - successful X profile retrieval
   - Wikipedia source retrieval
   - whether the relationship between the two
     is independently verified

6. Call the current network section
   "Mention Analysis".

7. Do NOT describe mentions as complete
   social relationships.

8. Topics and keywords are content signals.
   They are not definitive proof of interests.

9. If data was not retrieved, say:

   "Not available in the supplied dataset."

10. Do not say:

   "No information exists."

11. Rate limiting must be described as a
    technical collection limitation.

12. Do not claim an account is deleted,
    suspended, fake, private, or nonexistent
    unless the evidence specifically establishes it.

13. Do not provide an overall confidence score.

14. Keep the report professional and concise.

15. Do not reproduce raw JSON.

16. Do not include unnecessary historical facts.

17. Do not include unrelated Wikipedia information.

18. Distinguish observed data from interpretation.

19. Do not claim that a display name or bio
    independently proves the real-world identity
    of the account owner.

20. Do not describe internally consistent profile
    fields as independent identity verification.

21. When describing activity patterns, state that
    they are based on the retrieved tweet sample.

"""

    # -----------------------------------------------------
    # GENERATE TEXT REPORT
    # -----------------------------------------------------

    result = llm.invoke(
        prompt
    )

    report_text = result.content

    # -----------------------------------------------------
    # GENERATE PDF
    # -----------------------------------------------------

    report_generator = ReportGenerator()

    report_file = report_generator.generate_report(
        username=username,
        report_text=report_text,
        state=state
    )

    # -----------------------------------------------------
    # RETURN RESULTS TO LANGGRAPH
    # -----------------------------------------------------

    return {
        "final_report": report_text,
        "report_file": report_file
    }

