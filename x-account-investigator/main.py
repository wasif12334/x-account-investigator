from graph.investigator_graph import build_graph


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("X ACCOUNT INVESTIGATOR")
    print("=" * 60)

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    person_name = input(
        "\nEnter person's name: "
    ).strip()

    if not person_name:

        print(
            "Person name is required."
        )

        return

    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    print()

    print(
        f"Target person: {person_name}"
    )

    print()

    print(
        "Investigation pipeline:"
    )

    print(
        "  Person Name"
    )

    print(
        "      ↓"
    )

    print(
        "  Wikipedia"
    )

    print(
        "      ↓"
    )

    print(
        "  X Account Discovery"
    )

    print(
        "      ↓"
    )

    print(
        "  X Scraper"
    )

    print(
        "      ↓"
    )

    print(
        "  Profile / Network / Temporal / Topic"
    )

    print(
        "      ↓"
    )

    print(
        "  Verification"
    )

    print(
        "      ↓"
    )

    print(
        "  Final Report + PDF"
    )

    print()

    print(
        "Running LangGraph investigation..."
    )

    print(
        "Please wait...\n"
    )

    # -----------------------------------------------------
    # BUILD GRAPH
    # -----------------------------------------------------

    graph = build_graph()

    # -----------------------------------------------------
    # INITIAL STATE
    # -----------------------------------------------------

    initial_state = {

        "person_name":
            person_name,

        "username":
            "",

        "x_candidates":
            [],

        "discovered_handle":
            "",

        "discovery_confidence":
            0,

        "discovery_evidence":
            [],

        "wikipedia_data":
            {},

        "wikipedia_analysis":
            {},

        "x_data":
            {},

        "profile_analysis":
            {},

        "network_analysis":
            {},

        "temporal_analysis":
            {},

        "topic_analysis":
            {},

        "verification_analysis":
            {},

        "final_report":
            "",

        "report_file":
            ""
    }

    # -----------------------------------------------------
    # RUN
    # -----------------------------------------------------

    try:

        result = graph.invoke(
            initial_state
        )

    except Exception as e:

        print()
        print("=" * 60)
        print("INVESTIGATION FAILED")
        print("=" * 60)

        print()

        print(
            f"Error: {e}"
        )

        return

    # -----------------------------------------------------
    # COMPLETE
    # -----------------------------------------------------

    print()

    print("=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

    # -----------------------------------------------------
    # PERSON
    # -----------------------------------------------------

    print()

    print(
        f"Person: {person_name}"
    )

    # -----------------------------------------------------
    # DISCOVERED X ACCOUNT
    # -----------------------------------------------------

    handle = result.get(
        "discovered_handle",
        ""
    )

    confidence = result.get(
        "discovery_confidence",
        0
    )

    print()

    if handle:

        print(
            f"X Account: @{handle}"
        )

        print(
            f"Discovery Confidence: {confidence}"
        )

    else:

        print(
            "X Account: Not confidently discovered."
        )

        print(
            f"Discovery Confidence: {confidence}"
        )

    # -----------------------------------------------------
    # FINAL REPORT
    # -----------------------------------------------------

    print()

    print(
        "-" * 60
    )

    print(
        "FINAL REPORT"
    )

    print(
        "-" * 60
    )

    print()

    print(
        result.get(
            "final_report",
            "No report generated."
        )
    )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "PDF REPORT"
    )

    print(
        "=" * 60
    )

    print(
        result.get(
            "report_file",
            "No PDF generated."
        )
    )

    print(
        "=" * 60
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()