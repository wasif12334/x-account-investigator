from pathlib import Path

import matplotlib.pyplot as plt


# =========================================================
# CHART HELPERS
# =========================================================

NAVY = "#101828"
BLUE = "#175CD3"
BLUE_LIGHT = "#D1E9FF"
GRID = "#EAECF0"
TEXT = "#344054"
MUTED = "#667085"


def save_chart(fig, output_path):
    """
    Save matplotlib figure to disk.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(fig)

    return str(output_path)


# =========================================================
# DAY ACTIVITY
# =========================================================

def create_day_activity_chart(
    day_distribution,
    output_path,
):
    """
    Create activity-by-day bar chart.
    """

    if not day_distribution:
        return None

    days = list(
        day_distribution.keys()
    )

    values = [
        day_distribution[day]
        for day in days
    ]

    fig, ax = plt.subplots(
        figsize=(9, 3.6)
    )

    bars = ax.bar(
        days,
        values,
        width=0.62,
        color=BLUE,
    )

    # Title
    ax.set_title(
        "Observed Tweet Activity by Day",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        pad=14,
        loc="left",
    )

    ax.set_ylabel(
        "Tweets",
        fontsize=9,
        color=TEXT,
    )

    ax.tick_params(
        axis="x",
        labelsize=8,
        colors=TEXT,
    )

    ax.tick_params(
        axis="y",
        labelsize=8,
        colors=MUTED,
    )

    # Grid
    ax.grid(
        axis="y",
        color=GRID,
        linewidth=0.8,
        alpha=0.8,
    )

    ax.set_axisbelow(True)

    # Remove unnecessary borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

    # Value labels
    for bar, value in zip(
        bars,
        values,
    ):
        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height()
            + max(values, default=1) * 0.02,
            str(value),
            ha="center",
            va="bottom",
            fontsize=7.5,
            color=TEXT,
        )

    ax.margins(
        x=0.02
    )

    fig.tight_layout(
        pad=1.5
    )

    return save_chart(
        fig,
        output_path,
    )


# =========================================================
# HOUR ACTIVITY
# =========================================================

def create_hour_activity_chart(
    hour_distribution,
    output_path,
):
    """
    Create activity-by-hour chart.
    """

    if not hour_distribution:
        return None

    # Convert keys safely to integers
    normalized = {}

    for hour, value in hour_distribution.items():
        try:
            numeric_hour = int(
                str(hour).replace(
                    ":00",
                    "",
                )
            )

            normalized[numeric_hour] = value

        except (
            ValueError,
            TypeError,
        ):
            continue

    if not normalized:
        return None

    # Make sure all 24 hours are displayed
    hours = list(
        range(24)
    )

    values = [
        normalized.get(
            hour,
            0,
        )
        for hour in hours
    ]

    fig, ax = plt.subplots(
        figsize=(9, 3.8)
    )

    ax.plot(
        hours,
        values,
        marker="o",
        linewidth=2.2,
        markersize=4.5,
        color=BLUE,
    )

    # Fill area under line
    ax.fill_between(
        hours,
        values,
        alpha=0.10,
        color=BLUE,
    )

    ax.set_title(
        "Observed Tweet Activity by Hour",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        pad=14,
        loc="left",
    )

    ax.set_xlabel(
        "Hour (UTC)",
        fontsize=9,
        color=TEXT,
    )

    ax.set_ylabel(
        "Tweets",
        fontsize=9,
        color=TEXT,
    )

    ax.set_xticks(
        range(0, 24, 2)
    )

    ax.tick_params(
        axis="x",
        labelsize=8,
        colors=TEXT,
    )

    ax.tick_params(
        axis="y",
        labelsize=8,
        colors=MUTED,
    )

    ax.grid(
        axis="y",
        color=GRID,
        linewidth=0.8,
        alpha=0.8,
    )

    ax.grid(
        axis="x",
        color=GRID,
        linewidth=0.5,
        alpha=0.35,
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

    fig.tight_layout(
        pad=1.5
    )

    return save_chart(
        fig,
        output_path,
    )


# =========================================================
# MENTION CHART
# =========================================================

def create_mentions_chart(
    mentioned_accounts,
    output_path,
):
    """
    Create horizontal chart of most-mentioned accounts.
    """

    if not mentioned_accounts:
        return None

    data = mentioned_accounts[:8]

    if not data:
        return None

    # Reverse for horizontal ranking
    data = list(
        reversed(data)
    )

    labels = []

    values = []

    for item in data:
        username = item.get(
            "username",
            "unknown",
        )

        count = item.get(
            "count",
            0,
        )

        labels.append(
            f"@{username}"
        )

        values.append(
            count
        )

    fig, ax = plt.subplots(
        figsize=(9, 4.2)
    )

    bars = ax.barh(
        labels,
        values,
        color=BLUE,
        height=0.58,
    )

    ax.set_title(
        "Most Mentioned Accounts",
        fontsize=13,
        fontweight="bold",
        color=NAVY,
        pad=14,
        loc="left",
    )

    ax.set_xlabel(
        "Mention Events",
        fontsize=9,
        color=TEXT,
    )

    ax.tick_params(
        axis="y",
        labelsize=8,
        colors=TEXT,
    )

    ax.tick_params(
        axis="x",
        labelsize=8,
        colors=MUTED,
    )

    ax.grid(
        axis="x",
        color=GRID,
        linewidth=0.8,
        alpha=0.8,
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)

    # Add values at end of bars
    max_value = max(
        values,
        default=1,
    )

    for bar, value in zip(
        bars,
        values,
    ):
        ax.text(
            value
            + max_value * 0.025,
            bar.get_y()
            + bar.get_height() / 2,
            str(value),
            va="center",
            fontsize=8,
            color=TEXT,
        )

    ax.set_xlim(
        0,
        max_value * 1.18
        if max_value > 0
        else 1,
    )

    fig.tight_layout(
        pad=1.5
    )

    return save_chart(
        fig,
        output_path,
    )