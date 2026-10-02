from typing import TypedDict, Any


class InvestigatorState(TypedDict, total=False):
    username: str

    # Wikipedia
    wikipedia_data: Any
    wikipedia_analysis: Any

    # X data
    x_data: Any

    # Analysis
    profile_analysis: Any
    network_analysis: Any
    temporal_analysis: Any
    topic_analysis: Any

    # Verification + report
    verification_analysis: Any
    final_report: str
    report_file: str