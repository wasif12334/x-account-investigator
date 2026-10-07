import os

from reports.pdf_generator import ReportGenerator


# ==========================================================
# Utility
# ==========================================================

def safe(value, default="Not available"):

    if value is None:
        return default

    if value == "":
        return default

    return value


def normalize_confidence(value):

    """
    Some Wikipedia code may return:

        1.0

    while other agents return:

        100

    Convert Wikipedia-style 1.0 -> 100.
    """

    if value is None:
        return 0

    try:

        number = float(value)

        if 0 <= number <= 1:
            return round(
                number * 100,
                2
            )

        return round(
            number,
            2
        )

    except Exception:
        return value


# ==========================================================
# Report Agent
# ==========================================================

def report_agent(state):

    print(
        "      Generating final investigation report..."
    )

    # ------------------------------------------------------
    # Target
    # ------------------------------------------------------

    person_name = safe(
        state.get(
            "person_name"
        ),
        "Unknown target",
    )

    discovered_handle = (
        state.get(
            "discovered_handle"
        )
        or state.get(
            "username"
        )
        or ""
    )

    # ------------------------------------------------------
    # Wikipedia
    # ------------------------------------------------------

    wikipedia = (
        state.get(
            "wikipedia_data"
        )
        or {}
    )

    wikipedia_analysis = (
        state.get(
            "wikipedia_analysis"
        )
        or {}
    )

    wiki_status = (
        wikipedia.get(
            "status"
        )
        or wikipedia_analysis.get(
            "status"
        )
        or "unknown"
    )

    wiki_title = (
        wikipedia.get(
            "title"
        )
        or wikipedia_analysis.get(
            "title"
        )
        or person_name
    )

    wiki_summary = (
        wikipedia.get(
            "summary"
        )
        or wikipedia_analysis.get(
            "summary"
        )
        or ""
    )

    wiki_url = (
        wikipedia.get(
            "url"
        )
        or wikipedia_analysis.get(
            "url"
        )
        or ""
    )

    wiki_confidence_raw = (
        wikipedia.get(
            "confidence"
        )
    )

    if wiki_confidence_raw is None:

        wiki_confidence_raw = (
            wikipedia_analysis.get(
                "confidence"
            )
        )

    wiki_confidence = normalize_confidence(
        wiki_confidence_raw
    )

    # ------------------------------------------------------
    # X Discovery
    # ------------------------------------------------------

    candidates = (
        state.get(
            "x_candidates"
        )
        or []
    )

    discovery_confidence = (
        state.get(
            "discovery_confidence"
        )
        or 0
    )

    discovery_evidence = (
        state.get(
            "discovery_evidence"
        )
        or []
    )

    # ------------------------------------------------------
    # X Collection
    # ------------------------------------------------------

    x_data = (
        state.get(
            "x_data"
        )
        or {}
    )

    profile = (
        state.get(
            "profile"
        )
        or x_data.get(
            "profile"
        )
        or {}
    )

    tweets = (
        state.get(
            "tweets"
        )
        or x_data.get(
            "tweets"
        )
        or []
    )

    # ------------------------------------------------------
    # Analyses
    # ------------------------------------------------------

    profile_analysis = (
        state.get(
            "profile_analysis"
        )
        or {}
    )

    network = (
        state.get(
            "network_analysis"
        )
        or {}
    )

    temporal = (
        state.get(
            "temporal_analysis"
        )
        or {}
    )

    topics = (
        state.get(
            "topic_analysis"
        )
        or {}
    )

    verification = (
        state.get(
            "verification_analysis"
        )
        or {}
    )

    # ------------------------------------------------------
    # Ensure username exists
    # ------------------------------------------------------

    if not discovered_handle:

        discovered_handle = (
            profile.get(
                "username"
            )
            or ""
        )

    # ======================================================
    # BUILD ONE FINAL REPORT
    # ======================================================

    report = []

    report.append(
        "# X Account Investigation Report"
    )

    # ======================================================
    # 1. Executive Summary
    # ======================================================

    report.append(
        "\n## 1. Executive Summary"
    )

    report.append(
        f"\n**Investigation Target:** "
        f"{person_name}"
    )

    report.append(
        f"\n**Likely X Account:** "
        f"@{discovered_handle if discovered_handle else 'Not available'}"
    )

    report.append(
        f"\n**Discovery Confidence:** "
        f"{discovery_confidence}/100"
    )

    identity_score = verification.get(
        "identity_consistency",
        0,
    )

    identity_level = verification.get(
        "identity_level",
        "unknown",
    )

    ownership_score = verification.get(
        "ownership_evidence",
        0,
    )

    ownership_level = verification.get(
        "ownership_level",
        "unknown",
    )

    report.append(
        f"\n**Identity Consistency:** "
        f"{identity_score}/100 "
        f"({identity_level})"
    )

    report.append(
        f"\n**Ownership Evidence:** "
        f"{ownership_score}/100 "
        f"({ownership_level})"
    )

    report.append(
        "\nThe investigation combines Wikipedia identity "
        "information, X account discovery, public profile "
        "metadata, a collected tweet sample, network signals, "
        "temporal activity, topic signals, and identity "
        "verification."
    )

    # ======================================================
    # 2. Wikipedia Identity
    # ======================================================

    report.append(
        "\n## 2. Wikipedia Identity"
    )

    report.append(
        f"\n**Status:** {wiki_status}"
    )

    report.append(
        f"\n**Wikipedia Page:** "
        f"{wiki_title}"
    )

    report.append(
        f"\n**Wikipedia Confidence:** "
        f"{wiki_confidence}/100"
    )

    if wiki_url:

        report.append(
            f"\n**Wikipedia URL:** "
            f"{wiki_url}"
        )

    if wiki_summary:

        report.append(
            "\n### Background"
        )

        report.append(
            f"\n{wiki_summary}"
        )

    # ======================================================
    # 3. X Account Discovery
    # ======================================================

    report.append(
        "\n## 3. X Account Discovery"
    )

    if candidates:

        report.append(
            "\n| Rank | Handle | Score | Source |"
        )

        report.append(
            "|---:|---|---:|---|"
        )

        for index, candidate in enumerate(
            candidates[:10],
            start=1,
        ):

            if not isinstance(
                candidate,
                dict,
            ):
                continue

            username = (
                candidate.get(
                    "username"
                )
                or candidate.get(
                    "handle"
                )
                or ""
            )

            score = candidate.get(
                "score",
                0,
            )

            source = candidate.get(
                "source",
                "unknown",
            )

            report.append(
                f"| {index} | "
                f"@{username} | "
                f"{score}/100 | "
                f"{source} |"
            )

    else:

        report.append(
            "\nNo X discovery candidates were available."
        )

    # ------------------------------------------------------
    # Discovery evidence
    # ------------------------------------------------------

    if discovery_evidence:

        report.append(
            "\n### Best Candidate Evidence"
        )

        # Correct dictionary handling.
        #
        # Previous PDF printed:
        #
        # - status
        # - discovered_handle
        # - confidence
        #
        # because iterating a dictionary returns its KEYS.

        if isinstance(
            discovery_evidence,
            dict,
        ):

            best_candidate = (
                discovery_evidence.get(
                    "best_candidate"
                )
                or {}
            )

            evidence_list = (
                best_candidate.get(
                    "evidence"
                )
                if isinstance(
                    best_candidate,
                    dict,
                )
                else None
            )

            if not evidence_list:

                evidence_list = (
                    discovery_evidence.get(
                        "evidence"
                    )
                    or []
                )

        else:

            evidence_list = (
                discovery_evidence
            )

        if isinstance(
            evidence_list,
            list,
        ):

            for item in evidence_list:

                if isinstance(
                    item,
                    dict,
                ):

                    signal = item.get(
                        "signal",
                        item.get(
                            "name",
                            "evidence",
                        ),
                    )

                    points = item.get(
                        "points",
                        0,
                    )

                    explanation = (
                        item.get(
                            "explanation"
                        )
                        or item.get(
                            "reason"
                        )
                        or ""
                    )

                    report.append(
                        f"\n- **{signal}** "
                        f"({points} points): "
                        f"{explanation}"
                    )

                else:

                    report.append(
                        f"\n- {item}"
                    )

    # ======================================================
    # 4. X Profile
    # ======================================================

    report.append(
        "\n## 4. X Profile"
    )

    if profile:

        report.append(
            f"\n**Username:** "
            f"@{safe(profile.get('username'))}"
        )

        report.append(
            f"\n**Display Name:** "
            f"{safe(profile.get('display_name'))}"
        )

        report.append(
            f"\n**Bio:** "
            f"{safe(profile.get('bio'))}"
        )

        report.append(
            f"\n**Location:** "
            f"{safe(profile.get('location'))}"
        )

        report.append(
            f"\n**Followers:** "
            f"{safe(profile.get('followers'))}"
        )

        report.append(
            f"\n**Following:** "
            f"{safe(profile.get('following'))}"
        )

        report.append(
            f"\n**Posts Shown by Profile:** "
            f"{safe(profile.get('tweets_count'))}"
        )

        report.append(
            f"\n**Verified Indicator:** "
            f"{safe(profile.get('verified'))}"
        )

        report.append(
            f"\n**Created:** "
            f"{safe(profile.get('created'))}"
        )

        report.append(
            f"\n**Profile URL:** "
            f"{safe(profile.get('profile_url'))}"
        )

    else:

        report.append(
            "\nX profile information was not available."
        )

    # ======================================================
    # 5. Data Collection
    # ======================================================

    report.append(
        "\n## 5. Data Collection"
    )

    report.append(
        f"\n**Collection Status:** "
        f"{safe(x_data.get('status'))}"
    )

    report.append(
        f"\n**Profile Status:** "
        f"{safe(x_data.get('profile_status'))}"
    )

    report.append(
        f"\n**Tweet Status:** "
        f"{safe(x_data.get('tweet_status'))}"
    )

    report.append(
        f"\n**Tweets Requested:** "
        f"{safe(x_data.get('requested_tweets'))}"
    )

    # IMPORTANT:
    # Always use actual list length as fallback.

    collected_count = (
        x_data.get(
            "tweets_collected"
        )
    )

    if collected_count is None:

        collected_count = len(
            tweets
        )

    report.append(
        f"\n**Tweets Collected:** "
        f"{collected_count}"
    )

    report.append(
        f"\n**Collector Message:** "
        f"{safe(x_data.get('message'))}"
    )

    # ======================================================
    # 6. Network Analysis
    # ======================================================

    report.append(
        "\n## 6. Network Analysis"
    )

    network_tweets = network.get(
        "tweets_analyzed",
        len(tweets),
    )

    report.append(
        f"\n**Tweets Analyzed:** "
        f"{network_tweets}"
    )

    report.append(
        f"\n**Unique Mentioned Accounts:** "
        f"{network.get('unique_mentioned_accounts', 0)}"
    )

    report.append(
        f"\n**Mentions:** "
        f"{network.get('mentions', 0)}"
    )

    report.append(
        f"\n**Replies:** "
        f"{network.get('replies', 0)}"
    )

    report.append(
        f"\n**Retweets:** "
        f"{network.get('retweets', 0)}"
    )

    report.append(
        f"\n**Quotes:** "
        f"{network.get('quotes', 0)}"
    )

    top_accounts = (
        network.get(
            "top_accounts"
        )
        or []
    )

    if top_accounts:

        report.append(
            "\n### Most Frequent Interactions"
        )

        for account in top_accounts[:15]:

            if not isinstance(
                account,
                dict,
            ):
                continue

            username = account.get(
                "username",
                "",
            )

            count = account.get(
                "interactions",
                0,
            )

            report.append(
                f"\n- @{username}: "
                f"{count} interaction events"
            )

    # ======================================================
    # 7. Temporal Activity
    # ======================================================

    report.append(
        "\n## 7. Temporal Activity"
    )

    temporal_tweets = temporal.get(
        "tweets_analyzed",
        len(tweets),
    )

    report.append(
        f"\n**Tweets Analyzed:** "
        f"{temporal_tweets}"
    )

    report.append(
        f"\n**Timestamps Parsed:** "
        f"{temporal.get('timestamps_parsed', 0)}"
    )

    active_hour = temporal.get(
        "most_active_hour"
    )

    if active_hour is None:

        active_hour_display = (
            "Not available"
        )

    else:

        try:

            active_hour_display = (
                f"{int(active_hour):02d}:00 UTC"
            )

        except Exception:

            active_hour_display = (
                str(active_hour)
            )

    report.append(
        f"\n**Most Active Hour:** "
        f"{active_hour_display}"
    )

    report.append(
        f"\n**Most Active Day:** "
        f"{safe(temporal.get('most_active_day'))}"
    )

    # Day distribution

    day_distribution = (
        temporal.get(
            "day_distribution"
        )
        or {}
    )

    if day_distribution:

        report.append(
            "\n### Activity by Day"
        )

        report.append(
            "\n| Day | Tweets |"
        )

        report.append(
            "|---|---:|"
        )

        for day, count in (
            day_distribution.items()
        ):

            report.append(
                f"| {day} | {count} |"
            )

    # ======================================================
    # 8. Topics & Interests
    # ======================================================

    report.append(
        "\n## 8. Topics & Interests"
    )

    report.append(
        f"\n**Tweets Analyzed:** "
        f"{topics.get('tweets_analyzed', len(tweets))}"
    )

    keywords = (
        topics.get(
            "top_keywords"
        )
        or []
    )

    if keywords:

        report.append(
            "\n### Top Keywords"
        )

        for item in keywords[:20]:

            if isinstance(
                item,
                dict,
            ):

                word = item.get(
                    "keyword",
                    "",
                )

                count = item.get(
                    "count",
                    0,
                )

                report.append(
                    f"\n- {word}: {count}"
                )

    hashtags = (
        topics.get(
            "hashtags"
        )
        or []
    )

    if hashtags:

        report.append(
            "\n### Hashtags"
        )

        for item in hashtags[:20]:

            if isinstance(
                item,
                dict,
            ):

                tag = item.get(
                    "hashtag",
                    "",
                )

                count = item.get(
                    "count",
                    0,
                )

                report.append(
                    f"\n- {tag}: {count}"
                )

    # ======================================================
    # 9. Identity Verification
    # ======================================================

    report.append(
        "\n## 9. Identity Verification"
    )

    report.append(
        f"\n**Discovery Confidence:** "
        f"{verification.get('discovery_confidence', discovery_confidence)}/100"
    )

    report.append(
        f"\n**Identity Consistency:** "
        f"{identity_score}/100"
    )

    report.append(
        f"\n**Identity Level:** "
        f"{identity_level}"
    )

    report.append(
        f"\n**Ownership Evidence:** "
        f"{ownership_score}/100"
    )

    report.append(
        f"\n**Ownership Level:** "
        f"{ownership_level}"
    )

    evidence_matrix = (
        verification.get(
            "evidence_matrix"
        )
        or []
    )

    if evidence_matrix:

        report.append(
            "\n### Evidence Matrix"
        )

        report.append(
            "\n| Signal | Result | Points |"
        )

        report.append(
            "|---|---|---:|"
        )

        for item in evidence_matrix:

            if not isinstance(
                item,
                dict,
            ):
                continue

            report.append(
                f"| {item.get('signal', '')} | "
                f"{item.get('result', '')} | "
                f"{item.get('points', 0)} |"
            )

    assessment = verification.get(
        "assessment"
    )

    if assessment:

        report.append(
            "\n### Verification Assessment"
        )

        report.append(
            f"\n{assessment}"
        )

    # ======================================================
    # 10. Sources
    # ======================================================

    report.append(
        "\n## 10. Sources"
    )

    if profile.get(
        "profile_url"
    ):

        report.append(
            f"\n- X Account: "
            f"{profile.get('profile_url')}"
        )

    if wiki_url:

        report.append(
            f"\n- Wikipedia: "
            f"{wiki_url}"
        )

    report.append(
        "\n- X Collection: twscrape"
    )

    report.append(
        "\n- Workflow: LangGraph"
    )

    # ======================================================
    # 11. Limitations
    # ======================================================

    report.append(
        "\n## 11. Limitations"
    )

    report.append(
        "\n- Analysis is based only on information "
        "successfully retrieved during this investigation."
    )

    report.append(
        "\n- X data can change between investigation runs."
    )

    report.append(
        "\n- Tweet collection can be affected by X request "
        "limits and twscrape account availability."
    )

    report.append(
        "\n- The collected tweet sample is not the account's "
        "complete historical activity."
    )

    report.append(
        "\n- Mention frequency indicates observed interaction "
        "signals and is not a complete social-network graph."
    )

    report.append(
        "\n- Matching names, usernames, biographies, topics, "
        "or organizations do not independently prove account "
        "ownership."
    )

    report.append(
        "\n- Identity conclusions should be corroborated using "
        "independent public evidence."
    )

    # ======================================================
    # Final text
    # ======================================================

    report_text = "\n".join(
        report
    )

    # ======================================================
    # PDF
    # ======================================================

    report_file = ""

    try:

        output_directory = os.path.join(
            "reports",
            "output",
        )

        os.makedirs(
            output_directory,
            exist_ok=True,
        )

        safe_person_name = (
            person_name
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"{safe_person_name}"
            f"_investigation_report.pdf"
        )

        report_file = os.path.join(
            output_directory,
            filename,
        )

        generator = ReportGenerator()

        generator.generate_report(
            report_file,
            report_text,
        )

        print(
            "      PDF report created:"
        )

        print(
            f"      {report_file}"
        )

    except Exception as exc:

        print(
            f"      PDF generation failed: "
            f"{exc}"
        )

        report_file = ""

    return {
        "final_report": report_text,
        "report_file": report_file,
    }