from graph.investigator_graph import build_investigator_graph


def main():

    print()
    print("=" * 60)
    print("X ACCOUNT INVESTIGATOR")
    print("=" * 60)

    username = input(
        "\nEnter X username: "
    ).strip()

    username = username.replace("@", "")

    if not username:
        print("Username is required.")
        return

    print()
    print(f"Target: @{username}")

    print("\nRunning LangGraph investigation...")
    print("Please wait...\n")

    # -----------------------------------------------------
    # Build graph
    # -----------------------------------------------------

    graph = build_investigator_graph()

    # -----------------------------------------------------
    # Initial state
    # -----------------------------------------------------

    initial_state = {
        "username": username
    }

    # -----------------------------------------------------
    # Run investigation
    # -----------------------------------------------------

    result = graph.invoke(initial_state)

    # -----------------------------------------------------
    # Complete
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

    print("\nFINAL REPORT\n")

    print(
        result.get(
            "final_report",
            "No report generated."
        )
    )

    print()
    print("=" * 60)

    print("PDF REPORT:")

    print(
        result.get(
            "report_file",
            "No PDF generated."
        )
    )

    print("=" * 60)


if __name__ == "__main__":
    main()