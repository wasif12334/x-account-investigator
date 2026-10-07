from typing import TypedDict, Any, List, Dict


class InvestigatorState(TypedDict, total=False):

    # --------------------------------------------------
    # Investigation target
    # --------------------------------------------------

    person_name: str

    # --------------------------------------------------
    # Wikipedia
    # --------------------------------------------------

    wikipedia_data: Dict[str, Any]
    wikipedia_analysis: Dict[str, Any]

    # --------------------------------------------------
    # X discovery
    # --------------------------------------------------

    x_candidates: List[Dict[str, Any]]

    discovered_handle: str
    username: str

    discovery_confidence: float
    discovery_evidence: Any

    # --------------------------------------------------
    # X scraping
    # --------------------------------------------------

    x_data: Dict[str, Any]

    profile: Dict[str, Any]
    tweets: List[Dict[str, Any]]

    # --------------------------------------------------
    # Analysis
    # --------------------------------------------------

    profile_analysis: Dict[str, Any]
    network_analysis: Dict[str, Any]
    temporal_analysis: Dict[str, Any]
    topic_analysis: Dict[str, Any]

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    verification_analysis: Dict[str, Any]

    # --------------------------------------------------
    # Final report
    # --------------------------------------------------

    final_report: str
    report_file: str