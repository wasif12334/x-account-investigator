from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from datetime import datetime
import os


class ReportGenerator:

    def generate_report(
        self,
        username,
        profile_result,
        activity_result,
        identity_result,
        verification_result
    ):

        # Create reports folder
        os.makedirs("reports", exist_ok=True)

        filename = f"reports/{username}_investigation_report.pdf"

        document = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=35
        )

        # --------------------------------------------------
        # STYLES
        # --------------------------------------------------

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            "HeadingStyle",
            parent=styles["Heading2"],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            "NormalStyle",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12
        )

        small_style = ParagraphStyle(
            "SmallStyle",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10
        )

        story = []

        # ==================================================
        # TITLE
        # ==================================================

        story.append(
            Paragraph(
                "X ACCOUNT INVESTIGATION REPORT",
                title_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Username:</b> @{username}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Generated:</b> "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                normal_style
            )
        )

        story.append(Spacer(1, 10))

        # ==================================================
        # 1. PROFILE INFORMATION
        # ==================================================

        story.append(
            Paragraph(
                "1. PROFILE INFORMATION",
                heading_style
            )
        )

        profile_data = [
            ["Field", "Value"],
            ["Username", str(profile_result.username)],
            ["Display Name", str(profile_result.display_name)],
            ["Account Type", str(profile_result.account_type)],
            ["Followers", str(profile_result.followers)],
            ["Following", str(profile_result.following)],
            ["Post Count", str(profile_result.post_count)],
            ["Profile URL", str(profile_result.profile_url)],
        ]

        profile_table = Table(
            profile_data,
            colWidths=[1.5 * inch, 4.8 * inch]
        )

        profile_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 4),
            ])
        )

        story.append(profile_table)

        story.append(Spacer(1, 5))

        story.append(
            Paragraph(
                f"<b>Notable Information:</b> "
                f"{profile_result.notable_information}",
                small_style
            )
        )

        # ==================================================
        # 2. ACTIVITY ANALYSIS
        # ==================================================

        story.append(
            Paragraph(
                "2. ACTIVITY ANALYSIS",
                heading_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Recent Activity:</b> "
                f"{activity_result.recent_activity_summary}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Primary Topics:</b> "
                f"{activity_result.primary_topics}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Common Hashtags:</b> "
                f"{activity_result.common_hashtags}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Activity Patterns:</b> "
                f"{activity_result.activity_patterns}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Activity Confidence:</b> "
                f"{activity_result.confidence_level}",
                normal_style
            )
        )

        # ==================================================
        # 3. RECENT / NOTABLE POSTS
        # ==================================================

        story.append(
            Paragraph(
                "3. RECENT / NOTABLE POSTS",
                heading_style
            )
        )

        notable_posts = activity_result.notable_posts

        if notable_posts:

            for index, post in enumerate(
                notable_posts,
                start=1
            ):

                story.append(
                    Paragraph(
                        f"<b>{index}.</b> {post}",
                        small_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No notable posts were identified.",
                    small_style
                )
            )

        # ==================================================
        # 4. IDENTITY / OSINT
        # ==================================================

        story.append(
            Paragraph(
                "4. IDENTITY / OSINT FINDINGS",
                heading_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Professional Background:</b> "
                f"{identity_result.professional_background}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Organizations:</b> "
                f"{identity_result.organizations}",
                normal_style
            )
        )

        if hasattr(identity_result, "notable_information"):

            story.append(
                Paragraph(
                    f"<b>Notable Information:</b> "
                    f"{identity_result.notable_information}",
                    normal_style
                )
            )

        # ==================================================
        # 5. VERIFIED FINDINGS
        # ==================================================

        story.append(
            Paragraph(
                "5. VERIFIED FINDINGS",
                heading_style
            )
        )

        if verification_result.verified_findings:

            for finding in verification_result.verified_findings:

                story.append(
                    Paragraph(
                        f"• {finding}",
                        small_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No verified findings were produced.",
                    small_style
                )
            )

        # ==================================================
        # 6. CONFLICTING FINDINGS
        # ==================================================

        story.append(
            Paragraph(
                "6. CONFLICTING FINDINGS",
                heading_style
            )
        )

        if verification_result.conflicting_findings:

            for conflict in verification_result.conflicting_findings:

                story.append(
                    Paragraph(
                        f"• {conflict}",
                        small_style
                    )
                )

        else:

            story.append(
                Paragraph(
                    "No conflicts found.",
                    small_style
                )
            )

        # ==================================================
        # 7. CONFIDENCE SCORE
        # ==================================================

        story.append(
            Paragraph(
                "7. CONFIDENCE SCORE",
                heading_style
            )
        )

        story.append(
            Paragraph(
                f"<b>{verification_result.confidence_score}</b>",
                normal_style
            )
        )

        # ==================================================
        # 8. FINAL ASSESSMENT
        # ==================================================

        story.append(
            Paragraph(
                "8. FINAL ASSESSMENT",
                heading_style
            )
        )

        story.append(
            Paragraph(
                str(verification_result.final_assessment),
                normal_style
            )
        )

        # ==================================================
        # DISCLAIMER
        # ==================================================

        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                "<b>Disclaimer:</b> This report is generated from "
                "publicly available information collected by the "
                "investigation agents. Findings should be independently "
                "verified before being used for important decisions.",
                small_style
            )
        )

        # ==================================================
        # BUILD PDF
        # ==================================================

        document.build(story)

        return filename