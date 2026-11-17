
from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean, median, pstdev


# ============================================================
# CONFIGURATION
# ============================================================

DAY_NAMES = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

TIME_PERIODS = [
    "Morning", "Afternoon", "Evening", "Night"
]


# ============================================================
# GET TWEETS
# ============================================================

def get_tweets(state):
    tweets = state.get("tweets")

    if isinstance(tweets, list) and tweets:
        return tweets

    x_data = state.get("x_data") or {}
    tweets = x_data.get("tweets", [])

    return tweets if isinstance(tweets, list) else []


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(value):
    if not value:
        return None

    try:
        if isinstance(value, datetime):
            parsed = value

        elif isinstance(value, str):
            value = value.strip().replace("Z", "+00:00")

            if not value:
                return None

            parsed = datetime.fromisoformat(value)

        elif isinstance(value, (int, float)):
            # Support Unix timestamps.
            parsed = datetime.fromtimestamp(
                value,
                tz=timezone.utc
            )

        else:
            return None

        # Assume UTC only when timezone information is absent.
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    except (ValueError, TypeError, OverflowError, OSError):
        return None


def get_tweet_date(tweet):
    if not isinstance(tweet, dict):
        return None

    return (
        tweet.get("date")
        or tweet.get("created_at")
        or tweet.get("timestamp")
    )


# ============================================================
# TIME PERIOD
# ============================================================

def get_time_period(hour):
    if 5 <= hour <= 11:
        return "Morning"

    if 12 <= hour <= 16:
        return "Afternoon"

    if 17 <= hour <= 20:
        return "Evening"

    return "Night"


# ============================================================
# DAILY BURST DETECTION
# ============================================================

def detect_daily_bursts(daily_distribution):
    """
    Detect unusually high tweet counts on observed active days.

    Important:
    - Missing collection dates are not added as zero-post days.
    - At least 7 active dates are required.
    - This is a screening method, not proof of suspicious behavior.
    """

    if len(daily_distribution) < 7:
        return {
            "status": "insufficient_data",
            "reason": (
                "At least 7 active posting dates are required "
                "for daily burst screening."
            ),
            "baseline": None,
            "threshold": None,
            "unusual_days": [],
        }

    values = list(daily_distribution.values())

    baseline = median(values)

    deviations = [
        abs(value - baseline)
        for value in values
    ]

    mad = median(deviations)

    if mad == 0:
        threshold = max(
            baseline + 3,
            baseline * 2
        )
    else:
        threshold = baseline + (3 * 1.4826 * mad)

    unusual_days = []

    for date, count in daily_distribution.items():
        if count > threshold:
            unusual_days.append({
                "date": date,
                "tweets": count,
                "baseline": round(baseline, 2),
                "threshold": round(threshold, 2),
            })

    return {
        "status": "analyzed",
        "reason": (
            "Compared tweet counts across observed active dates "
            "using median and median absolute deviation."
        ),
        "baseline": round(baseline, 2),
        "threshold": round(threshold, 2),
        "unusual_days": unusual_days,
    }


# ============================================================
# HOURLY BURST DETECTION
# ============================================================

def detect_hourly_bursts(parsed_dates, active_day_count):
    """
    Screen for concentrated posting in individual UTC hours.

    Only hours containing tweets are compared. This avoids
    treating uncollected hours as confirmed zero-post hours.

    This method is a screening indicator, not a formal
    statistical anomaly detector.
    """

    if active_day_count < 7:
        return {
            "status": "insufficient_data",
            "reason": (
                "At least 7 active posting dates are required "
                "for hourly burst screening."
            ),
            "baseline": None,
            "threshold": None,
            "unusual_intervals": [],
        }

    hourly_counts = Counter()

    for date in parsed_dates:
        hour_start = date.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        hourly_counts[hour_start] += 1

    if len(hourly_counts) < 5:
        return {
            "status": "insufficient_data",
            "reason": (
                "Not enough distinct observed hourly intervals "
                "are available."
            ),
            "baseline": None,
            "threshold": None,
            "unusual_intervals": [],
        }

    values = list(hourly_counts.values())

    baseline = median(values)

    deviations = [
        abs(value - baseline)
        for value in values
    ]

    mad = median(deviations)

    if mad == 0:
        threshold = max(
            5,
            baseline + 3
        )
    else:
        threshold = max(
            5,
            baseline + (3 * 1.4826 * mad)
        )

    unusual_intervals = []

    for hour, count in hourly_counts.items():
        if count > threshold:
            unusual_intervals.append({
                "start": hour.isoformat(),
                "tweets": count,
                "baseline": round(baseline, 2),
                "threshold": round(threshold, 2),
            })

    unusual_intervals.sort(
        key=lambda item: item["tweets"],
        reverse=True
    )

    return {
        "status": "analyzed",
        "reason": (
            "Compared observed hourly tweet counts using "
            "median and median absolute deviation."
        ),
        "baseline": round(baseline, 2),
        "threshold": round(threshold, 2),
        "unusual_intervals": unusual_intervals[:10],
    }


# ============================================================
# TEMPORAL AGENT
# ============================================================

def temporal_agent(state):

    print("\n      Running Temporal Activity Analysis...")

    tweets = get_tweets(state)

    parsed_dates = []

    hour_counter = Counter()
    day_counter = Counter()
    period_counter = Counter()
    date_counter = Counter()

    # --------------------------------------------------------
    # PROCESS TWEETS
    # --------------------------------------------------------

    for tweet in tweets:

        if not isinstance(tweet, dict):
            continue

        parsed_date = parse_date(
            get_tweet_date(tweet)
        )

        if parsed_date is None:
            continue

        parsed_dates.append(parsed_date)

        hour_counter[parsed_date.hour] += 1

        day_counter[
            parsed_date.strftime("%A")
        ] += 1

        period_counter[
            get_time_period(parsed_date.hour)
        ] += 1

        date_counter[
            parsed_date.strftime("%Y-%m-%d")
        ] += 1

    valid_count = len(parsed_dates)

    # --------------------------------------------------------
    # NO VALID TIMESTAMPS
    # --------------------------------------------------------

    if valid_count == 0:

        result = {
            "status": "not_available",
            "tweets_received": len(tweets),
            "tweets_analyzed": 0,
            "timestamps_parsed": 0,
            "timezone": "UTC",
            "date_range": None,
            "active_days": 0,
            "calendar_days": 0,
            "hour_distribution": {},
            "day_distribution": {},
            "period_distribution": {},
            "daily_distribution": {},
            "most_active_hour": None,
            "most_active_day": None,
            "most_active_period": None,
            "activity_consistency": "Not available",
            "average_daily_tweets": None,
            "average_tweets_per_active_day": None,
            "daily_burst_analysis": {
                "status": "insufficient_data",
                "reason": "No valid timestamps were available.",
                "unusual_days": [],
            },
            "hourly_burst_analysis": {
                "status": "insufficient_data",
                "reason": "No valid timestamps were available.",
                "unusual_intervals": [],
            },
        }

        return {
            "temporal_analysis": result
        }

    # --------------------------------------------------------
    # DATE RANGE AND ACTIVE DAYS
    # --------------------------------------------------------

    earliest = min(parsed_dates)
    latest = max(parsed_dates)

    active_days = len(date_counter)

    calendar_days = (
        (latest.date() - earliest.date()).days + 1
    )

    # Only dates with observed tweets are included.
    # Missing dates are not assumed to have zero tweets.
    daily_distribution = dict(sorted(date_counter.items()))

    # --------------------------------------------------------
    # DISTRIBUTIONS
    # --------------------------------------------------------

    hour_distribution = {
        f"{hour:02d}:00": hour_counter.get(hour, 0)
        for hour in range(24)
    }

    day_distribution = {
        day: day_counter.get(day, 0)
        for day in DAY_NAMES
    }

    period_distribution = {
        period: period_counter.get(period, 0)
        for period in TIME_PERIODS
    }

    # --------------------------------------------------------
    # MOST ACTIVE PERIODS
    # --------------------------------------------------------

    most_active_hour = max(
        hour_counter,
        key=hour_counter.get
    )

    most_active_day = max(
        day_counter,
        key=day_counter.get
    )

    most_active_period = max(
        period_counter,
        key=period_counter.get
    )

    # --------------------------------------------------------
    # AVERAGES
    # --------------------------------------------------------

    average_per_active_day = round(
        valid_count / active_days,
        2
    )

    average_per_calendar_day = round(
        valid_count / calendar_days,
        2
    )

    # --------------------------------------------------------
    # ACTIVITY CONSISTENCY
    # --------------------------------------------------------

    daily_values = list(
        daily_distribution.values()
    )

    if len(daily_values) < 3:
        activity_consistency = "Insufficient data"

    else:
        daily_mean = mean(daily_values)

        variation = (
            pstdev(daily_values) / daily_mean
            if daily_mean else 0
        )

        if variation < 0.5:
            activity_consistency = "Relatively consistent"

        elif variation < 1.0:
            activity_consistency = "Moderately variable"

        else:
            activity_consistency = "Highly variable"

    # --------------------------------------------------------
    # BURST ANALYSIS
    # --------------------------------------------------------

    daily_bursts = detect_daily_bursts(
        daily_distribution
    )

    hourly_bursts = detect_hourly_bursts(
        parsed_dates,
        active_days
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    result = {
        "status": "success",

        "tweets_received": len(tweets),

        "tweets_analyzed": valid_count,

        "timestamps_parsed": valid_count,

        "timezone": "UTC",

        "date_range": {
            "start": earliest.isoformat(),
            "end": latest.isoformat(),
        },

        "active_days": active_days,

        "calendar_days": calendar_days,

        "hour_distribution": hour_distribution,

        "day_distribution": day_distribution,

        "period_distribution": period_distribution,

        "daily_distribution": daily_distribution,

        "most_active_hour": most_active_hour,

        "most_active_day": most_active_day,

        "most_active_period": most_active_period,

        "activity_consistency": activity_consistency,

        # Retained for compatibility with the earlier report.
        # This is the average across the complete calendar span.
        "average_daily_tweets": average_per_calendar_day,

        "average_tweets_per_active_day": average_per_active_day,

        "daily_burst_analysis": daily_bursts,

        "hourly_burst_analysis": hourly_bursts,

        "activity_bursts": daily_bursts["unusual_days"],

        "burst_detection_status": daily_bursts["status"],
    }

    # --------------------------------------------------------
    # CONSOLE OUTPUT
    # --------------------------------------------------------

    print("\n      ---------- TEMPORAL ANALYSIS ----------")

    print(f"      Tweets received: {len(tweets)}")

    print(f"      Valid timestamps: {valid_count}")

    print(f"      Active days: {active_days}")

    print(f"      Calendar days: {calendar_days}")

    print(
        f"      Date range: {earliest.date()} to {latest.date()}"
    )

    print(
        f"      Most active hour: {most_active_hour:02d}:00 UTC"
    )

    print(f"      Most active day: {most_active_day}")

    print(f"      Most active period: {most_active_period}")

    print(
        f"      Average per active day: {average_per_active_day}"
    )

    print(
        f"      Activity consistency: {activity_consistency}"
    )

    print(
        f"      Daily burst status: {daily_bursts['status']}"
    )

    print(
        f"      Hourly burst status: {hourly_bursts['status']}"
    )

    print("      ---------------------------------------")

    return {
        "temporal_analysis": result
    }
