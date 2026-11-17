
import os
import re

from reports.pdf_generator import ReportGenerator


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def safe(value, default="Not available"):
    if value is None or value == "":
        return default
    return value


def normalize_confidence(value):
    if value is None:
        return 0

    try:
        number = float(value)

        if 0 <= number <= 1:
            return round(number * 100, 2)

        return round(number, 2)

    except (ValueError, TypeError):
        return value


def format_percentage(value):
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return safe(value)


def get_list(data):
    return data if isinstance(data, list) else []


def get_dict(data):
    return data if isinstance(data, dict) else {}


def markdown_safe(value):
    return (
        str(safe(value))
        .replace("|", "\\|")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def format_count(value):
    if value is None:
        return "Metadata unavailable"
    return value


def format_distribution(distribution, title, report):
    distribution = get_dict(distribution)

    report.append(f"\n### {title}")

    if not distribution:
        report.append("\nNo distribution data available.")
        return

    report.append("\n| Category | Count |")
    report.append("|---|---:|")

    for category, count in distribution.items():
        report.append(
            f"| {markdown_safe(category)} | "
            f"{markdown_safe(count)} |"
        )


def format_burst_analysis(analysis, report, title):
    analysis = get_dict(analysis)

    report.append(f"\n### {title}")

    if not analysis:
        report.append("\nAnalysis information is unavailable.")
        return

    status = str(analysis.get("status", "unknown"))

    report.append(
        f"\n**Status:** {status.replace('_', ' ').title()}"
    )

    reason = analysis.get("reason")

    if reason:
        report.append(f"\n**Method Note:** {reason}")

    baseline = analysis.get("baseline")
    threshold = analysis.get("threshold")

    if baseline is not None:
        report.append(f"\n**Baseline:** {baseline}")

    if threshold is not None:
        report.append(f"\n**Threshold:** {threshold}")

    unusual_items = (
        analysis.get("unusual_days")
        or analysis.get("unusual_intervals")
        or []
    )

    unusual_items = get_list(unusual_items)

    if status.lower() != "analyzed":
        report.append(
            "\nThe available sample was insufficient for "
            "reliable burst screening. No conclusion about "
            "unusual activity can be made."
        )
        return

    if not unusual_items:
        report.append(
            "\nNo intervals exceeded the configured screening "
            "threshold in the analyzed sample."
        )
        return

    report.append(
        "\n| Date / Interval | Tweets | Baseline | Threshold |"
    )
    report.append("|---|---:|---:|---:|")

    for item in unusual_items[:15]:
        item = get_dict(item)

        label = (
            item.get("date")
            or item.get("start")
            or item.get("interval")
            or "Unknown"
        )

        report.append(
            f"| {markdown_safe(label)} | "
            f"{markdown_safe(item.get('tweets', 'N/A'))} | "
            f"{markdown_safe(item.get('baseline', 'N/A'))} | "
            f"{markdown_safe(item.get('threshold', 'N/A'))} |"
        )


def get_confidence_value(state, verification):
    value = verification.get("discovery_confidence")

    if value is None:
        value = state.get("discovery_confidence")

    return normalize_confidence(value)


def get_discovery_evidence(state):
    evidence = state.get("discovery_evidence") or []

    if isinstance(evidence, dict):
        best_candidate = get_dict(
            evidence.get("best_candidate")
        )

        evidence_list = get_list(
            best_candidate.get("evidence")
        )

        if not evidence_list:
            evidence_list = get_list(
                evidence.get("evidence")
            )

        return evidence_list

    return get_list(evidence)


def format_examples(examples, report, limit=5):
    examples = get_list(examples)

    if not examples:
        return

    report.append("\n**Representative Posts:**")

    for example in examples[:limit]:
        if isinstance(example, dict):
            example_text = (
                example.get("text")
                or example.get("tweet")
                or str(example)
            )

            matched_keywords = get_list(
                example.get("matched_keywords")
            )

        else:
            example_text = str(example)
            matched_keywords = []

        report.append(
            f"\n- {markdown_safe(example_text)}"
        )

        if matched_keywords:
            report.append(
                "\n  - Matching evidence: "
                + ", ".join(
                    markdown_safe(item)
                    for item in matched_keywords
                )
            )


def get_top_mentions(network):
    """
    Supports both NetworkAgent result formats:
        top_mentions
        top_accounts
    """

    accounts = (
        network.get("top_mentions")
        or network.get("top_accounts")
        or []
    )

    return get_list(accounts)


def get_mention_username(account):
    if isinstance(account, str):
        return account.lstrip("@")

    account = get_dict(account)

    return str(
        account.get("username")
        or account.get("handle")
        or account.get("screen_name")
        or ""
    ).lstrip("@")


def get_mention_count(account):
    if isinstance(account, dict):
        return (
            account.get("count")
            if account.get("count") is not None
            else account.get("mentions")
            if account.get("mentions") is not None
            else account.get("frequency")
            if account.get("frequency") is not None
            else account.get("interactions")
            if account.get("interactions") is not None
            else "N/A"
        )

    return "N/A"


def get_topic_percentage_basis(topics):
    return (
        topics.get("topic_percentages_basis")
        or topics.get("percentage_basis")
        or "All analyzed tweets"
    )


# ============================================================
# REPORT AGENT
# ============================================================

def report_agent(state):

    print("      Generating final investigation report...")

    state = get_dict(state)

    # ========================================================
    # TARGET
    # ========================================================

    target_name = safe(
        state.get("person_name")
        or state.get("target_name"),
        "Unknown target"
    )

    discovered_handle = (
        state.get("discovered_handle")
        or state.get("username")
        or ""
    )

    # ========================================================
    # WIKIPEDIA
    # ========================================================

    wikipedia = get_dict(
        state.get("wikipedia_data")
    )

    wikipedia_analysis = get_dict(
        state.get("wikipedia_analysis")
    )

    wiki_status = (
        wikipedia.get("status")
        or wikipedia_analysis.get("status")
        or "unknown"
    )

    wiki_title = (
        wikipedia.get("title")
        or wikipedia_analysis.get("title")
        or target_name
    )

    wiki_summary = (
        wikipedia.get("summary")
        or wikipedia_analysis.get("summary")
        or ""
    )

    wiki_url = (
        wikipedia.get("url")
        or wikipedia_analysis.get("url")
        or ""
    )

    wiki_confidence_raw = wikipedia.get("confidence")

    if wiki_confidence_raw is None:
        wiki_confidence_raw = wikipedia_analysis.get(
            "confidence"
        )

    wiki_confidence = normalize_confidence(
        wiki_confidence_raw
    )

    # ========================================================
    # DISCOVERY
    # ========================================================

    candidates = get_list(
        state.get("x_candidates")
    )

    discovery_confidence = normalize_confidence(
        state.get("discovery_confidence", 0)
    )

    discovery_evidence = get_discovery_evidence(state)

    # ========================================================
    # COLLECTION
    # ========================================================

    x_data = get_dict(
        state.get("x_data")
    )

    profile = get_dict(
        state.get("profile")
        or x_data.get("profile")
    )

    tweets = (
        state.get("tweets")
        or x_data.get("tweets")
        or []
    )

    tweets = get_list(tweets)

    # ========================================================
    # ANALYSES
    # ========================================================

    profile_analysis = get_dict(
        state.get("profile_analysis")
    )

    network = get_dict(
        state.get("network_analysis")
    )

    temporal = get_dict(
        state.get("temporal_analysis")
    )

    topics = get_dict(
        state.get("topic_analysis")
    )

    verification = get_dict(
        state.get("verification_analysis")
    )

    # ========================================================
    # USERNAME FALLBACK
    # ========================================================

    if not discovered_handle:
        discovered_handle = profile.get("username", "")

    discovered_handle = str(
        discovered_handle
    ).lstrip("@")

    # ========================================================
    # REPORT
    # ========================================================

    report = []

    report.append("# X Account Investigation Report")

    # ========================================================
    # 1. EXECUTIVE SUMMARY
    # ========================================================

    report.append("\n## 1. Executive Summary")

    report.append(
        f"\n**Investigation Target:** {markdown_safe(target_name)}"
    )

    report.append(
        f"\n**Likely X Account:** "
        f"@{markdown_safe(discovered_handle or 'Not available')}"
    )

    report.append(
        f"\n**Discovery Confidence:** "
        f"{discovery_confidence}/100"
    )

    identity_score = verification.get(
        "identity_consistency"
    )

    identity_level = verification.get(
        "identity_level",
        "unknown"
    )

    ownership_score = verification.get(
        "ownership_evidence"
    )

    ownership_level = verification.get(
        "ownership_level",
        "unknown"
    )

    report.append(
        f"\n**Identity Consistency:** "
        f"{safe(identity_score)}/100 ({identity_level})"
    )

    report.append(
        f"\n**Ownership Evidence:** "
        f"{safe(ownership_score)}/100 ({ownership_level})"
    )

    report.append(
        "\nThis investigation combines publicly available "
        "background information, X account discovery, profile "
        "metadata, collected posts, interaction signals, "
        "temporal activity analysis, topic classification, "
        "and identity verification."
    )

    report.append(
        "\nThe findings describe the available public information "
        "and the collected account activity. They do not "
        "independently establish the real-world identity or "
        "ownership of the investigated account."
    )

    # ========================================================
    # 2. WIKIPEDIA
    # ========================================================

    report.append("\n## 2. Wikipedia Identity")

    report.append(
        f"\n**Status:** {wiki_status}"
    )

    report.append(
        f"\n**Wikipedia Page:** {markdown_safe(wiki_title)}"
    )

    report.append(
        f"\n**Wikipedia Confidence:** {wiki_confidence}/100"
    )

    if wiki_url:
        report.append(
            f"\n**Wikipedia URL:** {wiki_url}"
        )

    if wiki_summary:
        report.append("\n### Background")
        report.append(f"\n{wiki_summary}")

    report.append(
        "\nA Wikipedia match provides background information "
        "only. It does not prove that the X account belongs to "
        "the person or organization described by the page."
    )

    # ========================================================
    # 3. ACCOUNT DISCOVERY
    # ========================================================

    report.append("\n## 3. X Account Discovery")

    if candidates:
        report.append(
            "\n| Rank | Handle | Score | Source |"
        )
        report.append("|---:|---|---:|---|")

        for index, candidate in enumerate(
            candidates[:10],
            start=1
        ):
            candidate = get_dict(candidate)

            if not candidate:
                continue

            username = (
                candidate.get("username")
                or candidate.get("handle")
                or ""
            )

            score = candidate.get("score", "N/A")
            source = candidate.get("source", "Unknown")

            report.append(
                f"| {index} | "
                f"@{markdown_safe(str(username).lstrip('@'))} | "
                f"{markdown_safe(score)} | "
                f"{markdown_safe(source)} |"
            )

    else:
        report.append(
            "\nNo X discovery candidates were available."
        )

    if discovery_evidence:
        report.append("\n### Best Candidate Evidence")

        report.append(
            "\nThe following signals contributed to the "
            "candidate evaluation:"
        )

        for item in discovery_evidence:
            if isinstance(item, dict):
                signal = (
                    item.get("signal")
                    or item.get("name")
                    or item.get("type")
                    or "Evidence"
                )

                points = item.get(
                    "points",
                    item.get("score", 0)
                )

                explanation = (
                    item.get("explanation")
                    or item.get("reason")
                    or item.get("description")
                    or item.get("details")
                    or "No explanation was provided."
                )

                report.append(
                    f"\n- **{markdown_safe(signal)}** "
                    f"({markdown_safe(points)} points): "
                    f"{markdown_safe(explanation)}"
                )

            else:
                report.append(
                    f"\n- {markdown_safe(item)}"
                )

    else:
        report.append(
            "\nNo detailed discovery evidence was supplied."
        )

    # ========================================================
    # 4. X PROFILE
    # ========================================================

    report.append("\n## 4. X Profile")

    if profile:
        report.append(
            f"\n**Username:** "
            f"@{markdown_safe(profile.get('username', 'Not available'))}"
        )

        report.append(
            f"\n**Display Name:** "
            f"{markdown_safe(profile.get('display_name'))}"
        )

        report.append(
            f"\n**Bio:** {markdown_safe(profile.get('bio'))}"
        )

        report.append(
            f"\n**Location:** {markdown_safe(profile.get('location'))}"
        )

        report.append(
            f"\n**Followers:** {markdown_safe(profile.get('followers'))}"
        )

        report.append(
            f"\n**Following:** {markdown_safe(profile.get('following'))}"
        )

        report.append(
            f"\n**Posts Shown by Profile:** "
            f"{markdown_safe(profile.get('tweets_count'))}"
        )

        report.append(
            f"\n**Verified Indicator:** "
            f"{markdown_safe(profile.get('verified'))}"
        )

        report.append(
            f"\n**Created:** {markdown_safe(profile.get('created'))}"
        )

        report.append(
            f"\n**Profile URL:** "
            f"{markdown_safe(profile.get('profile_url'))}"
        )

        report.append(
            "\nThe verified indicator reflects the metadata "
            "returned by the collector. A False value does not "
            "by itself establish that an account is fake."
        )

    else:
        report.append(
            "\nX profile information was not available."
        )

    # ========================================================
    # 5. DATA COLLECTION
    # ========================================================

    report.append("\n## 5. Data Collection")

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

    collected_count = x_data.get("tweets_collected")

    if collected_count is None:
        collected_count = len(tweets)

    report.append(
        f"\n**Tweets Collected:** {collected_count}"
    )

    report.append(
        f"\n**Collector Message:** "
        f"{safe(x_data.get('message'))}"
    )

    # ========================================================
    # 6. NETWORK ANALYSIS
    # ========================================================

    report.append("\n## 6. Network Analysis")

    report.append(
        f"\n**Tweets Analyzed:** "
        f"{network.get('tweets_analyzed', len(tweets))}"
    )

    unique_accounts = network.get(
        "unique_mentioned_accounts",
        network.get("unique_accounts", 0)
    )

    report.append(
        f"\n**Unique Mentioned Accounts:** "
        f"{safe(unique_accounts)}"
    )

    # Critical compatibility fix:
    # New NetworkAgent uses mention_count.
    # Older ReportAgent expected mentions.

    total_mentions = network.get("mentions")

    if total_mentions is None:
        total_mentions = network.get("mention_count")

    report.append(
        f"\n**Total Mentions:** "
        f"{format_count(total_mentions)}"
    )

    replies = network.get("replies")
    retweets = network.get("retweets")
    quotes = network.get("quotes")

    report.append(
        f"\n**Replies:** {format_count(replies)}"
    )

    report.append(
        f"\n**Retweets:** {format_count(retweets)}"
    )

    report.append(
        f"\n**Quotes:** {format_count(quotes)}"
    )

    top_accounts = get_top_mentions(network)

    if top_accounts:
        report.append("\n### Most Frequently Mentioned Accounts")

        report.append(
            "\n| Rank | Account | Mention Count |"
        )

        report.append(
            "|---:|---|---:|"
        )

        for index, account in enumerate(
            top_accounts[:20],
            start=1
        ):
            username = get_mention_username(account)
            count = get_mention_count(account)

            if not username:
                continue

            report.append(
                f"| {index} | "
                f"@{markdown_safe(username)} | "
                f"{markdown_safe(count)} |"
            )

    if network:
        report.append(
            "\nMention counts indicate references detected in "
            "the collected posts. They do not necessarily prove "
            "direct communication, a relationship, or a reply."
        )

        availability = get_dict(
            network.get("metadata_availability")
        )

        if availability:
            report.append(
                "\n**Interaction Metadata Availability:**"
            )

            for key, value in availability.items():
                report.append(
                    f"\n- {markdown_safe(key.replace('_', ' ').title())}: "
                    f"{markdown_safe(value)}"
                )

        analysis_note = network.get("analysis_note")

        if analysis_note:
            report.append(
                f"\n**Analysis Note:** {markdown_safe(analysis_note)}"
            )

    else:
        report.append(
            "\nNetwork analysis information was not available. "
            "Missing counts must not be interpreted as proof "
            "that no interactions occurred."
        )

    # ========================================================
    # 7. TEMPORAL ACTIVITY
    # ========================================================

    report.append("\n## 7. Temporal Activity")

    report.append(
        f"\n**Tweets Analyzed:** "
        f"{temporal.get('tweets_analyzed', len(tweets))}"
    )

    report.append(
        f"\n**Timestamps Parsed:** "
        f"{temporal.get('timestamps_parsed', 0)}"
    )

    timezone = temporal.get("timezone", "UTC")

    report.append(
        f"\n**Timezone:** {timezone}"
    )

    date_range = get_dict(
        temporal.get("date_range")
    )

    if date_range:
        report.append(
            f"\n**Observation Start:** "
            f"{safe(date_range.get('start'))}"
        )

        report.append(
            f"\n**Observation End:** "
            f"{safe(date_range.get('end'))}"
        )

    report.append(
        f"\n**Active Posting Days:** "
        f"{safe(temporal.get('active_days'))}"
    )

    report.append(
        f"\n**Calendar Days in Date Range:** "
        f"{safe(temporal.get('calendar_days'))}"
    )

    active_hour = temporal.get("most_active_hour")

    if active_hour is None:
        active_hour_display = "Not available"
    else:
        try:
            active_hour_display = (
                f"{int(active_hour):02d}:00 {timezone}"
            )
        except (ValueError, TypeError):
            active_hour_display = str(active_hour)

    report.append(
        f"\n**Most Active Hour:** {active_hour_display}"
    )

    report.append(
        f"\n**Most Active Day:** "
        f"{safe(temporal.get('most_active_day'))}"
    )

    report.append(
        f"\n**Most Active Period:** "
        f"{safe(temporal.get('most_active_period'))}"
    )

    report.append(
        f"\n**Observed Active-Day Consistency:** "
        f"{safe(temporal.get('activity_consistency'))}"
    )

    report.append(
        f"\n**Average Tweets per Calendar Day:** "
        f"{safe(temporal.get('average_daily_tweets'))}"
    )

    report.append(
        f"\n**Average Tweets per Active Day:** "
        f"{safe(temporal.get('average_tweets_per_active_day'))}"
    )

    report.append(
        "\nThese statistics describe the timestamps in the "
        "retrieved sample. They should not be interpreted as "
        "continuous monitoring or reliable long-term posting "
        "rates when collection is incomplete."
    )

    format_distribution(
        temporal.get("hour_distribution"),
        f"Activity by Hour ({timezone})",
        report
    )

    format_distribution(
        temporal.get("day_distribution"),
        f"Activity by Day of Week ({timezone})",
        report
    )

    format_distribution(
        temporal.get("period_distribution"),
        f"Activity by Time Period ({timezone})",
        report
    )

    daily_distribution = get_dict(
        temporal.get("daily_distribution")
    )

    if daily_distribution:
        report.append("\n### Daily Posting Activity")

        report.append(
            "\nOnly dates with observed tweets are displayed. "
            "Missing dates are not assumed to have zero posts."
        )

        report.append("\n| Date | Tweets |")
        report.append("|---|---:|")

        sorted_daily = sorted(
            daily_distribution.items(),
            key=lambda item: str(item[0])
        )

        for date, count in sorted_daily[-31:]:
            report.append(
                f"| {markdown_safe(date)} | "
                f"{markdown_safe(count)} |"
            )

        if len(sorted_daily) > 31:
            report.append(
                f"\n*Showing the latest 31 active dates "
                f"out of {len(sorted_daily)}.*"
            )

    else:
        report.append(
            "\nDaily posting distribution is unavailable."
        )

    format_burst_analysis(
        temporal.get("daily_burst_analysis"),
        report,
        "Daily Activity Burst Screening"
    )

    format_burst_analysis(
        temporal.get("hourly_burst_analysis"),
        report,
        "Hourly Activity Burst Screening"
    )

    # ========================================================
    # 8. TOPICS AND CONTENT THEMES
    # ========================================================

    report.append("\n## 8. Topics and Content Themes")

    analyzed_topics = topics.get(
        "tweets_analyzed",
        0
    )

    classified_tweets = topics.get(
        "classified_tweets"
    )

    unclassified_tweets = topics.get(
        "unclassified_tweets"
    )

    coverage = topics.get(
        "classification_coverage_percentage"
    )

    report.append(
        f"\n**Tweets Analyzed:** {analyzed_topics}"
    )

    report.append(
        f"\n**Topics Detected:** "
        f"{topics.get('topics_detected', 0)}"
    )

    if classified_tweets is not None:
        report.append(
            f"\n**Classified Tweets:** {classified_tweets}"
        )

    if unclassified_tweets is not None:
        report.append(
            f"\n**Unclassified Tweets:** {unclassified_tweets}"
        )

    if coverage is not None:
        report.append(
            f"\n**Classification Coverage:** "
            f"{format_percentage(coverage)}"
        )

    report.append(
        f"\n**Analysis Method:** "
        f"{safe(topics.get('analysis_method'))}"
    )

    report.append(
        "\nThe categories below represent themes detected "
        "in published posts. They do not establish the personal "
        "beliefs or interests of an account owner."
    )

    report.append(
        "\nA tweet may be assigned to more than one category. "
        "Topic percentages may therefore overlap."
    )

    percentage_basis = get_topic_percentage_basis(topics)

    report.append(
        f"\n**Percentage Basis:** {percentage_basis}"
    )

    percentage_note = topics.get("percentage_note")

    if percentage_note:
        report.append(f"\n{percentage_note}")

    primary_interests = get_list(
        topics.get("primary_interests")
    )

    secondary_interests = get_list(
        topics.get("secondary_interests")
    )

    topic_groups = get_list(
        topics.get("topic_groups")
    )

    # Avoid presenting a weakly supported topic as a confirmed
    # primary interest.

    if primary_interests:
        report.append("\n### Most Frequently Detected Themes")

        report.append(
            "\nThese are the highest-ranked categories produced "
            "by the classifier, not verified personal interests."
        )

        for interest in primary_interests:
            interest = get_dict(interest)

            topic_name = interest.get(
                "topic",
                "Unknown Topic"
            )

            description = interest.get(
                "description",
                ""
            )

            tweet_count = interest.get(
                "tweet_count",
                0
            )

            percentage = interest.get("percentage")

            report.append(
                f"\n#### {markdown_safe(topic_name)}"
            )

            if description:
                report.append(
                    f"\n{markdown_safe(description)}"
                )

            report.append(
                f"\n**Related Tweets:** {tweet_count}"
            )

            if percentage is not None:
                report.append(
                    f"\n**Percentage:** "
                    f"{format_percentage(percentage)}"
                )

    if secondary_interests:
        report.append("\n### Other Detected Themes")

        report.append(
            "\n| Topic | Related Tweets | Percentage |"
        )
        report.append("|---|---:|---:|")

        for interest in secondary_interests:
            interest = get_dict(interest)

            topic_name = interest.get(
                "topic",
                "Unknown"
            )

            tweet_count = interest.get(
                "tweet_count",
                0
            )

            percentage = interest.get("percentage")

            percentage_display = (
                format_percentage(percentage)
                if percentage is not None
                else "N/A"
            )

            report.append(
                f"| {markdown_safe(topic_name)} | "
                f"{markdown_safe(tweet_count)} | "
                f"{markdown_safe(percentage_display)} |"
            )

    if topic_groups:
        report.append("\n### Detailed Topic Analysis")

        for topic in topic_groups:
            topic = get_dict(topic)

            topic_name = topic.get(
                "topic",
                "Unknown Topic"
            )

            description = topic.get(
                "description",
                ""
            )

            tweet_count = topic.get(
                "tweet_count",
                0
            )

            percentage = topic.get("percentage")

            report.append(
                f"\n#### {markdown_safe(topic_name)}"
            )

            if description:
                report.append(
                    f"\n{markdown_safe(description)}"
                )

            report.append(
                f"\n**Related Tweets:** {tweet_count}"
            )

            if percentage is not None:
                report.append(
                    f"\n**Percentage:** "
                    f"{format_percentage(percentage)}"
                )

            supporting_keywords = get_list(
                topic.get("supporting_keywords")
            )

            if supporting_keywords:
                keyword_names = []

                for item in supporting_keywords:
                    if isinstance(item, dict):
                        keyword = item.get("keyword")
                        if keyword:
                            keyword_names.append(str(keyword))
                    else:
                        keyword_names.append(str(item))

                if keyword_names:
                    report.append(
                        "\n**Supporting Keywords:** "
                        + ", ".join(
                            markdown_safe(item)
                            for item in keyword_names
                        )
                    )

            format_examples(
                topic.get("representative_tweets"),
                report,
                limit=5
            )

    keywords = get_list(
        topics.get("top_keywords")
    )

    if keywords:
        report.append("\n### Top Keywords")

        report.append("\n| Keyword | Frequency |")
        report.append("|---|---:|")

        for item in keywords[:20]:
            item = get_dict(item)

            report.append(
                f"| {markdown_safe(item.get('keyword', ''))} | "
                f"{markdown_safe(item.get('count', 0))} |"
            )

    hashtags = get_list(
        topics.get("hashtags")
    )

    if hashtags:
        report.append("\n### Frequently Used Hashtags")

        report.append("\n| Hashtag | Frequency |")
        report.append("|---|---:|")

        for item in hashtags[:20]:
            item = get_dict(item)

            tag = str(
                item.get("hashtag", "")
            ).lstrip("#")

            report.append(
                f"| #{markdown_safe(tag)} | "
                f"{markdown_safe(item.get('count', 0))} |"
            )

    if not any([
        primary_interests,
        secondary_interests,
        topic_groups,
        keywords,
        hashtags
    ]):
        report.append(
            "\nNo topic or keyword information was available."
        )

    if coverage is not None:
        try:
            coverage_number = float(coverage)

            if coverage_number < 30:
                report.append(
                    "\n**Classification Caution:** The classifier "
                    "covered only a limited portion of the "
                    "analyzed posts. The detected themes should "
                    "be treated as preliminary rather than a "
                    "complete representation of the account's content."
                )
        except (ValueError, TypeError):
            pass

    # ========================================================
    # 9. IDENTITY VERIFICATION
    # ========================================================

    report.append("\n## 9. Identity Verification")

    verification_discovery_confidence = get_confidence_value(
        state,
        verification
    )

    report.append(
        f"\n**Discovery Confidence:** "
        f"{verification_discovery_confidence}/100"
    )

    report.append(
        f"\n**Identity Consistency:** "
        f"{safe(identity_score)}/100"
    )

    report.append(
        f"\n**Identity Level:** {identity_level}"
    )

    report.append(
        f"\n**Ownership Evidence:** "
        f"{safe(ownership_score)}/100"
    )

    report.append(
        f"\n**Ownership Level:** {ownership_level}"
    )

    evidence_matrix = get_list(
        verification.get("evidence_matrix")
    )

    if evidence_matrix:
        report.append("\n### Evidence Matrix")

        report.append(
            "\n| Signal | Result | Points |"
        )
        report.append("|---|---|---:|")

        for item in evidence_matrix:
            item = get_dict(item)

            report.append(
                f"| {markdown_safe(item.get('signal', ''))} | "
                f"{markdown_safe(item.get('result', ''))} | "
                f"{markdown_safe(item.get('points', 0))} |"
            )

    assessment = verification.get("assessment")

    if assessment:
        report.append("\n### Verification Assessment")
        report.append(f"\n{markdown_safe(assessment)}")

    report.append(
        "\nDiscovery confidence measures how strongly the "
        "candidate matched the search criteria. It should not "
        "be treated as independent proof of account ownership."
    )

    # ========================================================
    # 10. SOURCES AND TECHNOLOGY
    # ========================================================

    report.append("\n## 10. Sources and Technology")

    profile_url = profile.get("profile_url")

    if profile_url:
        report.append(
            f"\n- X Account: {profile_url}"
        )

    if wiki_url:
        report.append(
            f"\n- Wikipedia: {wiki_url}"
        )

    report.append("\n- X Collection: twscrape")
    report.append("\n- Workflow Orchestration: LangGraph")
    report.append(
        "\n- Temporal and topic analysis: Custom Python agents"
    )

    # ========================================================
    # 11. LIMITATIONS
    # ========================================================

    report.append("\n## 11. Limitations")

    limitations = [
        "Analysis is based only on information successfully retrieved during this investigation.",
        "X data can change between investigation runs.",
        "Tweet collection may be affected by request limits, network conditions and scraper availability.",
        "The collected sample does not necessarily represent the account's complete historical activity.",
        "A partial collection should not be interpreted as a complete representation of the account.",
        "Temporal patterns describe the timestamps in the collected sample, not necessarily long-term posting habits.",
        "Dates without collected tweets are not automatically treated as dates with zero posting activity.",
        "Average posting rates can be misleading when the collection period contains large observation gaps.",
        "Burst screening does not prove automation, suspicious behavior or malicious activity.",
        "Topic classification depends on predefined rules and may contain false positives and false negatives.",
        "Unclassified tweets may contain meaningful subjects that are not covered by the current topic taxonomy.",
        "Topic categories may overlap because one post can discuss several subjects.",
        "Mention frequency is not a complete representation of an account's social network.",
        "Missing interaction metadata can result in incomplete network statistics.",
        "Mentioning an account does not necessarily establish direct communication or a relationship.",
        "Matching names, usernames, biographies, topics or organizations do not independently prove account ownership.",
        "Identity conclusions should be corroborated using independent public evidence."
    ]

    for limitation in limitations:
        report.append(
            f"\n- {limitation}"
        )

    # ========================================================
    # FINAL REPORT TEXT
    # ========================================================

    report_text = "\n".join(report)

    # ========================================================
    # PDF GENERATION
    # ========================================================

    report_file = ""

    try:
        output_directory = os.path.join(
            "reports",
            "output"
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        safe_target_name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            str(target_name).strip().lower()
        ).strip("_")

        if not safe_target_name:
            safe_target_name = "unknown_target"

        filename = (
            f"{safe_target_name}_investigation_report.pdf"
        )

        report_file = os.path.join(
            output_directory,
            filename
        )

        generator = ReportGenerator()

        generator.generate_report(
            report_file,
            report_text
        )

        print("\n      PDF report created:")
        print(f"      {report_file}")

    except Exception as exc:
        print(
            f"\n      PDF generation failed: {exc}"
        )

        report_file = ""

    # ========================================================
    # LANGGRAPH OUTPUT
    # ========================================================

    return {
        "final_report": report_text,
        "report_file": report_file
    }
