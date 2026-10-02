from datetime import datetime
from pathlib import Path
import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)

from reports.charts import (
    create_day_activity_chart,
    create_hour_activity_chart,
    create_mentions_chart,
)


PAGE_WIDTH, PAGE_HEIGHT = A4


# =========================================================
# FONT
# =========================================================

def register_fonts():

    candidates = [

        (
            "DejaVuSans",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),

        (
            "DejaVuSans-Bold",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ),

        (
            "Arial",
            "C:/Windows/Fonts/arial.ttf"
        ),

        (
            "Arial-Bold",
            "C:/Windows/Fonts/arialbd.ttf"
        ),
    ]

    registered = set()

    for name, path in candidates:

        if Path(path).exists():

            try:

                pdfmetrics.registerFont(
                    TTFont(
                        name,
                        path
                    )
                )

                registered.add(
                    name
                )

            except Exception:

                pass

    if "DejaVuSans" in registered:

        return (

            "DejaVuSans",

            (
                "DejaVuSans-Bold"
                if "DejaVuSans-Bold"
                in registered
                else "DejaVuSans"
            ),
        )

    if "Arial" in registered:

        return (

            "Arial",

            (
                "Arial-Bold"
                if "Arial-Bold"
                in registered
                else "Arial"
            ),
        )

    return (
        "Helvetica",
        "Helvetica-Bold"
    )


BODY_FONT, BOLD_FONT = register_fonts()


# =========================================================
# HELPERS
# =========================================================

def escape(value):

    if value in (
        None,
        ""
    ):

        value = "Not available"

    return html.escape(
        str(value)
    )


def safe_filename(value):

    return re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        value
    )


def clean_markdown(text):

    text = str(
        text or ""
    )

    text = text.replace(
        "**",
        ""
    )

    text = text.replace(
        "__",
        ""
    )

    text = text.replace(
        "###",
        ""
    )

    text = text.replace(
        "##",
        ""
    )

    text = text.replace(
        "#",
        ""
    )

    return text.strip()


# =========================================================
# HEADER / FOOTER
# =========================================================

def draw_header_footer(
    canvas,
    doc,
    username
):

    canvas.saveState()

    canvas.setStrokeColor(
        colors.HexColor(
            "#D9DEE7"
        )
    )

    canvas.line(
        18 * mm,
        PAGE_HEIGHT - 16 * mm,
        PAGE_WIDTH - 18 * mm,
        PAGE_HEIGHT - 16 * mm,
    )

    canvas.setFont(
        BODY_FONT,
        7.5
    )

    canvas.setFillColor(
        colors.HexColor(
            "#667085"
        )
    )

    canvas.drawString(
        18 * mm,
        PAGE_HEIGHT - 12 * mm,
        "X ACCOUNT INVESTIGATOR"
    )

    canvas.drawRightString(
        PAGE_WIDTH - 18 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.drawString(
        18 * mm,
        10 * mm,
        (
            f"@{username}  •  "
            f"{datetime.now().strftime('%Y-%m-%d')}"
        )
    )

    canvas.restoreState()


# =========================================================
# REPORT GENERATOR
# =========================================================

class ReportGenerator:

    def __init__(
        self,
        output_dir="reports/output"
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        styles = getSampleStyleSheet()

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        self.title = ParagraphStyle(

            "ReportTitle",

            fontName=BOLD_FONT,

            fontSize=25,

            leading=30,

            textColor=
                colors.HexColor(
                    "#111827"
                ),

            alignment=TA_CENTER,

            spaceAfter=8,
        )

        # -------------------------------------------------
        # Subtitle
        # -------------------------------------------------

        self.subtitle = ParagraphStyle(

            "ReportSubtitle",

            fontName=BODY_FONT,

            fontSize=11,

            leading=16,

            textColor=
                colors.HexColor(
                    "#667085"
                ),

            alignment=TA_CENTER,
        )

        # -------------------------------------------------
        # Heading
        # -------------------------------------------------

        self.h1 = ParagraphStyle(

            "H1",

            fontName=BOLD_FONT,

            fontSize=17,

            leading=21,

            textColor=
                colors.HexColor(
                    "#111827"
                ),

            spaceBefore=5,

            spaceAfter=10,
        )

        # -------------------------------------------------
        # Subheading
        # -------------------------------------------------

        self.h2 = ParagraphStyle(

            "H2",

            fontName=BOLD_FONT,

            fontSize=11,

            leading=14,

            textColor=
                colors.HexColor(
                    "#344054"
                ),

            spaceBefore=6,

            spaceAfter=5,
        )

        # -------------------------------------------------
        # Body
        # -------------------------------------------------

        self.body = ParagraphStyle(

            "Body",

            fontName=BODY_FONT,

            fontSize=9.3,

            leading=14,

            textColor=
                colors.HexColor(
                    "#344054"
                ),

            spaceAfter=6,
        )

        # -------------------------------------------------
        # Small
        # -------------------------------------------------

        self.small = ParagraphStyle(

            "Small",

            fontName=BODY_FONT,

            fontSize=7.8,

            leading=11,

            textColor=
                colors.HexColor(
                    "#667085"
                ),
        )

        # -------------------------------------------------
        # Card value
        # -------------------------------------------------

        self.card_value = ParagraphStyle(

            "CardValue",

            fontName=BOLD_FONT,

            fontSize=16,

            leading=19,

            textColor=
                colors.HexColor(
                    "#111827"
                ),

            alignment=TA_CENTER,
        )

        # -------------------------------------------------
        # Card label
        # -------------------------------------------------

        self.card_label = ParagraphStyle(

            "CardLabel",

            fontName=BODY_FONT,

            fontSize=7.5,

            leading=10,

            textColor=
                colors.HexColor(
                    "#667085"
                ),

            alignment=TA_CENTER,
        )

    # =====================================================
    # CARD
    # =====================================================

    def card(
        self,
        value,
        label
    ):

        table = Table(

            [
                [

                    Paragraph(
                        escape(value),
                        self.card_value
                    ),

                    Paragraph(
                        escape(label),
                        self.card_label
                    ),
                ]
            ],

            colWidths=[
                36 * mm
            ],

            rowHeights=[
                22 * mm
            ],
        )

        table.setStyle(

            TableStyle(

                [

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ),

                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor(
                            "#E4E7EC"
                        ),
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        return table

    # =====================================================
    # STATUS
    # =====================================================

    def status_badge(
        self,
        label,
        status
    ):

        status = str(
            status
        ).upper()

        if status in {
            "SUCCESS",
            "FOUND",
            "OK"
        }:

            bg = "#ECFDF3"
            fg = "#027A48"

        elif status in {
            "RATE_LIMITED",
            "REVIEW",
            "PARTIAL"
        }:

            bg = "#FFFAEB"
            fg = "#B54708"

        elif status in {
            "ERROR",
            "NOT_FOUND"
        }:

            bg = "#FEF3F2"
            fg = "#B42318"

        else:

            bg = "#F2F4F7"
            fg = "#475467"

        table = Table(

            [[

                Paragraph(
                    f"<b>{escape(label)}</b>",
                    self.small
                ),

                Paragraph(
                    f"<b>{escape(status)}</b>",
                    self.small
                ),

            ]],

            colWidths=[
                55 * mm,
                28 * mm
            ],
        )

        table.setStyle(

            TableStyle(

                [

                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, 0),
                        colors.HexColor(bg),
                    ),

                    (
                        "TEXTCOLOR",
                        (1, 0),
                        (1, 0),
                        colors.HexColor(fg),
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        return table

    # =====================================================
    # KEY VALUE TABLE
    # =====================================================

    def key_value_table(
        self,
        rows
    ):

        data = []

        for key, value in rows:

            data.append(

                [

                    Paragraph(
                        f"<b>{escape(key)}</b>",
                        self.small
                    ),

                    Paragraph(
                        escape(value),
                        self.small
                    ),
                ]
            )

        table = Table(

            data,

            colWidths=[
                42 * mm,
                125 * mm
            ],
        )

        table.setStyle(

            TableStyle(

                [

                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor(
                            "#EAECF0"
                        ),
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        return table

    # =====================================================
    # MARKDOWN
    # =====================================================

    def markdown_to_flowables(
        self,
        text
    ):

        elements = []

        for raw_line in str(
            text or ""
        ).splitlines():

            line = raw_line.strip()

            if not line:

                elements.append(
                    Spacer(
                        1,
                        4
                    )
                )

                continue

            clean = clean_markdown(
                line
            )

            if re.match(
                r"^\d+\.\s+",
                clean
            ):

                clean = re.sub(
                    r"^\d+\.\s+",
                    "",
                    clean
                )

                elements.append(

                    Paragraph(
                        escape(clean),
                        self.h2
                    )
                )

            elif clean.startswith(
                "- "
            ):

                elements.append(

                    Paragraph(
                        "• "
                        + escape(
                            clean[2:]
                        ),
                        self.body
                    )
                )

            elif clean.startswith(
                "• "
            ):

                elements.append(

                    Paragraph(
                        escape(clean),
                        self.body
                    )
                )

            else:

                elements.append(

                    Paragraph(
                        escape(clean),
                        self.body
                    )
                )

        return elements

    # =====================================================
    # CHARTS
    # =====================================================

    def build_charts(
        self,
        state,
        chart_dir
    ):

        chart_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        temporal = state.get(
            "temporal_analysis",
            {}
        )

        network = state.get(
            "network_analysis",
            {}
        )

        charts = []

        # Day chart
        day_distribution = temporal.get(
            "day_distribution",
            {}
        )

        if day_distribution:

            path = create_day_activity_chart(

                day_distribution,

                chart_dir
                / "activity_by_day.png"
            )

            charts.append(
                (
                    "Activity by Day",
                    path
                )
            )

        # Hour chart
        hour_distribution = temporal.get(
            "hour_distribution",
            {}
        )

        if hour_distribution:

            path = create_hour_activity_chart(

                hour_distribution,

                chart_dir
                / "activity_by_hour.png"
            )

            charts.append(
                (
                    "Activity by Hour",
                    path
                )
            )

        # Mention chart
        mentions = network.get(
            "mentioned_accounts",
            []
        )

        if mentions:

            path = create_mentions_chart(

                mentions,

                chart_dir
                / "top_mentions.png"
            )

            if path:

                charts.append(
                    (
                        "Top Mentioned Accounts",
                        path
                    )
                )

        return charts

    # =====================================================
    # GENERATE REPORT
    # =====================================================

    def generate_report(
        self,
        username,
        report_text,
        state=None
    ):

        state = state or {}

        filename = (

            self.output_dir
            / f"{safe_filename(username)}"
            "_investigation_report.pdf"
        )

        document = SimpleDocTemplate(

            str(filename),

            pagesize=A4,

            rightMargin=18 * mm,

            leftMargin=18 * mm,

            topMargin=23 * mm,

            bottomMargin=17 * mm,

            title=
                f"X Account Investigation - "
                f"@{username}",

            author=
                "X Account Investigator",
        )

        story = []

        # =================================================
        # COVER PAGE
        # =================================================

        story.extend(

            [

                Spacer(
                    1,
                    32 * mm
                ),

                Paragraph(
                    "X ACCOUNT",
                    self.title
                ),

                Paragraph(
                    "INVESTIGATION REPORT",
                    self.title
                ),

                Spacer(
                    1,
                    6
                ),

                Paragraph(
                    f"@{escape(username)}",
                    self.subtitle
                ),

                Spacer(
                    1,
                    20 * mm
                ),
            ]
        )

        cover_table = Table(

            [

                [

                    Paragraph(
                        "<b>Investigation Framework</b>",
                        self.small
                    ),

                    Paragraph(
                        "LangGraph",
                        self.small
                    ),
                ],

                [

                    Paragraph(
                        "<b>Primary Sources</b>",
                        self.small
                    ),

                    Paragraph(
                        "X + Wikipedia",
                        self.small
                    ),
                ],

                [

                    Paragraph(
                        "<b>Tweet Sample</b>",
                        self.small
                    ),

                    Paragraph(
                        escape(
                            state
                            .get(
                                "x_data",
                                {}
                            )
                            .get(
                                "tweets_collected",
                                0
                            )
                        ),
                        self.small
                    ),
                ],

                [

                    Paragraph(
                        "<b>Generated</b>",
                        self.small
                    ),

                    Paragraph(
                        datetime.now()
                        .strftime(
                            "%d %B %Y, %H:%M"
                        ),
                        self.small
                    ),
                ],
            ],

            colWidths=[
                55 * mm,
                100 * mm
            ],
        )

        cover_table.setStyle(

            TableStyle(

                [

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#F8FAFC"
                        ),
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        colors.HexColor(
                            "#E4E7EC"
                        ),
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ]
            )
        )

        story.append(
            cover_table
        )

        story.append(
            Spacer(
                1,
                30 * mm
            )
        )

        story.append(

            Paragraph(

                "Automated public-source analysis report. "
                "Findings are limited to evidence successfully "
                "retrieved during the investigation.",

                self.small
            )
        )

        story.append(
            PageBreak()
        )

        # =================================================
        # DASHBOARD
        # =================================================

        story.append(
            Paragraph(
                "Investigation Overview",
                self.h1
            )
        )

        x_data = state.get(
            "x_data",
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

        wiki = state.get(
            "wikipedia_analysis",
            {}
        )

        cards = [

            self.card(
                x_data.get(
                    "tweets_collected",
                    0
                ),
                "TWEETS ANALYZED"
            ),

            self.card(
                network.get(
                    "interaction_count",
                    0
                ),
                "MENTION EVENTS"
            ),

            self.card(
                network.get(
                    "unique_accounts",
                    0
                ),
                "UNIQUE ACCOUNTS"
            ),

            self.card(
                profile.get(
                    "followers",
                    "N/A"
                ),
                "FOLLOWERS"
            ),
        ]

        dashboard = Table(

            [cards],

            colWidths=[
                41 * mm
            ] * 4
        )

        dashboard.setStyle(

            TableStyle(

                [

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        2
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        2
                    ),
                ]
            )
        )

        story.append(
            dashboard
        )

        story.append(
            Spacer(
                1,
                10
            )
        )

        # =================================================
        # STATUS
        # =================================================

        story.append(
            Paragraph(
                "Collection Status",
                self.h2
            )
        )

        statuses = [

            self.status_badge(
                "X Profile",
                x_data.get(
                    "profile_status",
                    "unknown"
                )
            ),

            self.status_badge(
                "Tweets",
                x_data.get(
                    "tweets_status",
                    "unknown"
                )
            ),

            self.status_badge(
                "Wikipedia",
                wiki.get(
                    "status",
                    "unknown"
                )
            ),

            self.status_badge(
                "Temporal",
                temporal.get(
                    "status",
                    "unknown"
                )
            ),

            self.status_badge(
                "Mentions",
                network.get(
                    "status",
                    "unknown"
                )
            ),
        ]

        status_table = Table(

            [

                [
                    statuses[0],
                    statuses[1]
                ],

                [
                    statuses[2],
                    statuses[3]
                ],

                [
                    statuses[4],
                    ""
                ],
            ],

            colWidths=[
                90 * mm,
                90 * mm
            ]
        )

        status_table.setStyle(

            TableStyle(

                [

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                ]
            )
        )

        story.append(
            status_table
        )

        # =================================================
        # EXECUTIVE SUMMARY
        # =================================================

        story.append(
            Spacer(
                1,
                10
            )
        )

        story.append(
            Paragraph(
                "Executive Summary",
                self.h1
            )
        )

        executive = ""

        for line in str(
            report_text
        ).splitlines():

            if line.strip().startswith(
                "1. Executive Summary"
            ):
                continue

            if line.strip().startswith(
                "2. Subject Identification"
            ):
                break

            if line.strip():

                executive += (
                    line.strip()
                    + " "
                )

        story.extend(
            self.markdown_to_flowables(
                executive.strip()
            )
        )

        story.append(
            PageBreak()
        )

        # =================================================
        # SUBJECT IDENTIFICATION
        # =================================================

        story.append(
            Paragraph(
                "Subject Identification",
                self.h1
            )
        )

        profile_rows = [

            (
                "X Username",
                f"@{profile.get('username', username)}"
            ),

            (
                "Display Name",
                profile.get(
                    "display_name",
                    "Not available"
                )
            ),

            (
                "X Profile URL",
                profile.get(
                    "profile_url",
                    "Not available"
                )
            ),

            (
                "Wikipedia Retrieval",
                wiki.get(
                    "status",
                    "Not available"
                )
            ),

            (
                "Wikipedia URL",
                state
                .get(
                    "wikipedia_data",
                    {}
                )
                .get(
                    "url",
                    "Not available"
                )
            ),
        ]

        story.append(
            self.key_value_table(
                profile_rows
            )
        )

        story.append(
            Spacer(
                1,
                10
            )
        )

        story.append(

            Paragraph(

                "Identity note: successful retrieval of an "
                "X profile and a Wikipedia page does not, "
                "by itself, establish common ownership or identity.",

                self.small
            )
        )

        story.append(
            PageBreak()
        )

        # =================================================
        # X PROFILE
        # =================================================

        story.append(
            Paragraph(
                "X Profile",
                self.h1
            )
        )

        story.append(

            self.key_value_table(

                [

                    (
                        "Username",
                        profile.get(
                            "username",
                            "Not available"
                        )
                    ),

                    (
                        "Display Name",
                        profile.get(
                            "display_name",
                            "Not available"
                        )
                    ),

                    (
                        "Bio",
                        profile.get(
                            "bio",
                            "Not available"
                        )
                    ),

                    (
                        "Location",
                        profile.get(
                            "location",
                            "Not available"
                        )
                    ),

                    (
                        "Followers",
                        profile.get(
                            "followers",
                            "Not available"
                        )
                    ),

                    (
                        "Following",
                        profile.get(
                            "following",
                            "Not available"
                        )
                    ),

                    (
                        "Posts",
                        profile.get(
                            "tweets_count",
                            "Not available"
                        )
                    ),

                    (
                        "Verified",
                        profile.get(
                            "verified",
                            "Not available"
                        )
                    ),

                    (
                        "Created",
                        profile.get(
                            "created",
                            "Not available"
                        )
                    ),
                ]
            )
        )

        # =================================================
        # MENTION ANALYSIS
        # =================================================

        story.append(
            Spacer(
                1,
                12
            )
        )

        story.append(
            Paragraph(
                "Mention Analysis",
                self.h1
            )
        )

        story.append(

            self.key_value_table(

                [

                    (
                        "Tweets analyzed",
                        network.get(
                            "total_tweets_analyzed",
                            0
                        )
                    ),

                    (
                        "Mention events",
                        network.get(
                            "interaction_count",
                            0
                        )
                    ),

                    (
                        "Unique accounts",
                        network.get(
                            "unique_accounts",
                            0
                        )
                    ),
                ]
            )
        )

        mentions = network.get(
            "mentioned_accounts",
            []
        )

        if mentions:

            story.append(
                Spacer(
                    1,
                    8
                )
            )

            mention_data = [

                [

                    Paragraph(
                        "<b>Account</b>",
                        self.small
                    ),

                    Paragraph(
                        "<b>Mentions</b>",
                        self.small
                    ),
                ]
            ]

            for item in mentions:

                mention_data.append(

                    [

                        Paragraph(
                            "@"
                            + escape(
                                item.get(
                                    "username"
                                )
                            ),
                            self.small
                        ),

                        Paragraph(
                            escape(
                                item.get(
                                    "count"
                                )
                            ),
                            self.small
                        ),
                    ]
                )

            table = Table(

                mention_data,

                colWidths=[
                    120 * mm,
                    40 * mm
                ]
            )

            table.setStyle(

                TableStyle(

                    [

                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#F2F4F7"
                            )
                        ),

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.35,
                            colors.HexColor(
                                "#EAECF0"
                            )
                        ),

                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            7
                        ),

                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            7
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            5
                        ),
                    ]
                )
            )

            story.append(
                table
            )

        story.append(
            PageBreak()
        )

        # =================================================
        # TEMPORAL
        # =================================================

        story.append(
            Paragraph(
                "Temporal Activity",
                self.h1
            )
        )

        story.append(

            self.key_value_table(

                [

                    (
                        "Tweets analyzed",
                        temporal.get(
                            "total_tweets",
                            0
                        )
                    ),

                    (
                        "Timestamps analyzed",
                        temporal.get(
                            "timestamps_analyzed",
                            0
                        )
                    ),

                    (
                        "Most active day",
                        temporal.get(
                            "most_active_day",
                            "Not available"
                        )
                    ),

                    (
                        "Most active hour",
                        temporal.get(
                            "most_active_hour",
                            "Not available"
                        )
                    ),
                ]
            )
        )

        chart_dir = (

            self.output_dir
            / f"{safe_filename(username)}_charts"
        )

        charts = self.build_charts(
            state,
            chart_dir
        )

        for title, path in charts:

            if (
                "Activity by Day"
                in title
                or
                "Activity by Hour"
                in title
            ):

                story.append(
                    Spacer(
                        1,
                        10
                    )
                )

                story.append(
                    Paragraph(
                        title,
                        self.h2
                    )
                )

                story.append(

                    Image(
                        path,
                        width=165 * mm,
                        height=66 * mm
                    )
                )

        story.append(
            PageBreak()
        )

        # =================================================
        # TOPICS
        # =================================================

        story.append(
            Paragraph(
                "Topics & Interests",
                self.h1
            )
        )

        topics = state.get(
            "topic_analysis",
            {}
        )

        story.extend(

            self.markdown_to_flowables(

                topics.get(
                    "summary",
                    ""
                )
            )
        )

        hashtags = topics.get(
            "hashtags",
            []
        )

        keywords = topics.get(
            "keywords",
            []
        )

        if hashtags:

            story.append(
                Paragraph(
                    "Observed Hashtags",
                    self.h2
                )
            )

            hashtag_text = (
                " • ".join(

                    f"#{item.get('hashtag')} "
                    f"({item.get('count')})"

                    for item in hashtags[:10]
                )
            )

            story.append(

                Paragraph(
                    escape(
                        hashtag_text
                    ),
                    self.body
                )
            )

        if keywords:

            story.append(
                Paragraph(
                    "Observed Keywords",
                    self.h2
                )
            )

            keyword_text = (
                " • ".join(

                    f"{item.get('keyword')} "
                    f"({item.get('count')})"

                    for item in keywords[:15]
                )
            )

            story.append(

                Paragraph(
                    escape(
                        keyword_text
                    ),
                    self.body
                )
            )

        story.append(

            Paragraph(

                "Interpretation note: keyword and hashtag "
                "frequency describes content signals within "
                "the collected sample. It does not independently "
                "prove personal interests.",

                self.small
            )
        )

        # =================================================
        # WIKIPEDIA
        # =================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "Wikipedia Background",
                self.h1
            )
        )

        story.extend(

            self.markdown_to_flowables(

                state
                .get(
                    "wikipedia_analysis",
                    {}
                )
                .get(
                    "summary",
                    ""
                )
            )
        )

        # =================================================
        # VERIFICATION
        # =================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "Verification & Evidence",
                self.h1
            )
        )

        story.extend(

            self.markdown_to_flowables(

                state
                .get(
                    "verification_analysis",
                    {}
                )
                .get(
                    "summary",
                    ""
                )
            )
        )

        # =================================================
        # LIMITATIONS
        # =================================================

        story.append(
            Spacer(
                1,
                12
            )
        )

        story.append(
            Paragraph(
                "Data Collection Limitations",
                self.h1
            )
        )

        limitations = [

            "Analysis is based only on data successfully retrieved during this investigation.",

            "Tweet availability can be affected by X request limits and scraper account availability.",

            "The requested tweet count is configurable and the report identifies the actual retrieved sample.",

            "Mention analysis is not a complete social-network graph.",

            "The retrieved tweet sample does not represent the account's complete historical activity.",

            "A Wikipedia source and an X account do not independently prove common ownership.",
        ]

        for item in limitations:

            story.append(

                Paragraph(
                    "• " + escape(item),
                    self.body
                )
            )

        # =================================================
        # SOURCES
        # =================================================

        story.append(
            Spacer(
                1,
                10
            )
        )

        story.append(
            Paragraph(
                "Sources",
                self.h1
            )
        )

        x_url = profile.get(
            "profile_url",
            f"https://x.com/{username}"
        )

        wiki_url = (
            state
            .get(
                "wikipedia_data",
                {}
            )
            .get(
                "url",
                "Not available"
            )
        )

        source_rows = [

            (
                "X Account",
                x_url
            ),

            (
                "Wikipedia",
                wiki_url
            ),

            (
                "X Collection",
                "twscrape"
            ),

            (
                "Workflow",
                "LangGraph"
            ),
        ]

        story.append(

            self.key_value_table(
                source_rows
            )
        )

        # =================================================
        # BUILD
        # =================================================

        document.build(

            story,

            onFirstPage=lambda canvas, doc:
                draw_header_footer(
                    canvas,
                    doc,
                    username
                ),

            onLaterPages=lambda canvas, doc:
                draw_header_footer(
                    canvas,
                    doc,
                    username
                ),
        )

        return str(
            filename
        )