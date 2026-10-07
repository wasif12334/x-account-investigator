import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


class ReportGenerator:

    def __init__(self):

        self.styles = getSampleStyleSheet()

        # --------------------------------------------------
        # Custom styles
        # --------------------------------------------------

        self.title_style = ParagraphStyle(
            "InvestigationTitle",
            parent=self.styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            alignment=TA_CENTER,
            spaceAfter=15,
        )

        self.heading1_style = ParagraphStyle(
            "Heading1Custom",
            parent=self.styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            spaceBefore=12,
            spaceAfter=8,
        )

        self.heading2_style = ParagraphStyle(
            "Heading2Custom",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            spaceBefore=10,
            spaceAfter=6,
        )

        self.body_style = ParagraphStyle(
            "BodyCustom",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            spaceAfter=6,
        )

        self.bullet_style = ParagraphStyle(
            "BulletCustom",
            parent=self.body_style,
            leftIndent=14,
            firstLineIndent=-7,
            bulletIndent=5,
            spaceAfter=4,
        )

        self.small_style = ParagraphStyle(
            "SmallCustom",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
        )

    # ======================================================
    # Helpers
    # ======================================================

    def clean_markdown(self, text):
        """
        Convert simple Markdown styling into ReportLab-supported tags.
        """

        if text is None:
            return ""

        text = str(text)

        # Escape XML-sensitive characters first
        text = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        # Bold Markdown:
        # **text** -> <b>text</b>
        text = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            text,
        )

        # Inline code
        text = re.sub(
            r"`(.+?)`",
            r"<font name='Courier'>\1</font>",
            text,
        )

        return text

    def parse_markdown_table(self, lines, start_index):
        """
        Parse Markdown table such as:

        | Rank | Handle | Score |
        |---:|---|---:|
        | 1 | @abc | 90 |
        """

        rows = []

        index = start_index

        while index < len(lines):

            line = lines[index].strip()

            if not line.startswith("|"):
                break

            cells = [
                cell.strip()
                for cell in line.strip("|").split("|")
            ]

            # Skip separator row:
            # |---|---|---|
            separator = True

            for cell in cells:

                value = (
                    cell
                    .replace("-", "")
                    .replace(":", "")
                    .strip()
                )

                if value:
                    separator = False
                    break

            if not separator:
                rows.append(cells)

            index += 1

        return rows, index

    # ======================================================
    # Page decoration
    # ======================================================

    def add_page_number(self, canvas, doc):

        canvas.saveState()

        width, height = A4

        canvas.setFont(
            "Helvetica",
            8,
        )

        canvas.drawString(
            20 * mm,
            10 * mm,
            "X ACCOUNT INVESTIGATOR",
        )

        canvas.drawRightString(
            width - 20 * mm,
            10 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    # ======================================================
    # Main PDF generation
    # ======================================================

    def generate_report(
        self,
        output_path,
        report_text,
    ):

        if not report_text:
            raise ValueError(
                "report_text cannot be empty."
            )

        output_directory = os.path.dirname(
            output_path
        )

        if output_directory:
            os.makedirs(
                output_directory,
                exist_ok=True,
            )

        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,

            rightMargin=18 * mm,
            leftMargin=18 * mm,

            topMargin=18 * mm,
            bottomMargin=18 * mm,

            title="X Account Investigation Report",
            author="X Account Investigator",
        )

        story = []

        lines = report_text.splitlines()

        index = 0

        while index < len(lines):

            raw_line = lines[index]

            line = raw_line.strip()

            # ----------------------------------------------
            # Empty line
            # ----------------------------------------------

            if not line:

                story.append(
                    Spacer(
                        1,
                        3,
                    )
                )

                index += 1
                continue

            # ----------------------------------------------
            # Main title
            # ----------------------------------------------

            if line.startswith("# "):

                title = line[2:].strip()

                story.append(
                    Spacer(
                        1,
                        8,
                    )
                )

                story.append(
                    Paragraph(
                        self.clean_markdown(
                            title
                        ),
                        self.title_style,
                    )
                )

                story.append(
                    Spacer(
                        1,
                        8,
                    )
                )

                index += 1
                continue

            # ----------------------------------------------
            # Section heading
            # ----------------------------------------------

            if line.startswith("## "):

                heading = line[3:].strip()

                story.append(
                    Paragraph(
                        self.clean_markdown(
                            heading
                        ),
                        self.heading1_style,
                    )
                )

                index += 1
                continue

            # ----------------------------------------------
            # Subheading
            # ----------------------------------------------

            if line.startswith("### "):

                heading = line[4:].strip()

                story.append(
                    Paragraph(
                        self.clean_markdown(
                            heading
                        ),
                        self.heading2_style,
                    )
                )

                index += 1
                continue

            # ----------------------------------------------
            # Markdown table
            # ----------------------------------------------

            if line.startswith("|"):

                table_rows, next_index = (
                    self.parse_markdown_table(
                        lines,
                        index,
                    )
                )

                if table_rows:

                    formatted_rows = []

                    for row_index, row in enumerate(
                        table_rows
                    ):

                        formatted_row = []

                        for cell in row:

                            style = (
                                self.small_style
                            )

                            if row_index == 0:

                                formatted_row.append(
                                    Paragraph(
                                        f"<b>{self.clean_markdown(cell)}</b>",
                                        style,
                                    )
                                )

                            else:

                                formatted_row.append(
                                    Paragraph(
                                        self.clean_markdown(
                                            cell
                                        ),
                                        style,
                                    )
                                )

                        formatted_rows.append(
                            formatted_row
                        )

                    column_count = max(
                        len(row)
                        for row in formatted_rows
                    )

                    available_width = (
                        A4[0]
                        - (36 * mm)
                    )

                    column_width = (
                        available_width
                        / column_count
                    )

                    table = Table(
                        formatted_rows,
                        colWidths=[
                            column_width
                        ] * column_count,
                        repeatRows=1,
                        hAlign="LEFT",
                    )

                    table.setStyle(
                        TableStyle(
                            [
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, 0),
                                    colors.HexColor(
                                        "#E8E8E8"
                                    ),
                                ),
                                (
                                    "TEXTCOLOR",
                                    (0, 0),
                                    (-1, 0),
                                    colors.black,
                                ),
                                (
                                    "FONTNAME",
                                    (0, 0),
                                    (-1, 0),
                                    "Helvetica-Bold",
                                ),
                                (
                                    "GRID",
                                    (0, 0),
                                    (-1, -1),
                                    0.5,
                                    colors.HexColor(
                                        "#B0B0B0"
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
                                    5,
                                ),
                                (
                                    "RIGHTPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    5,
                                ),
                                (
                                    "TOPPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    5,
                                ),
                                (
                                    "BOTTOMPADDING",
                                    (0, 0),
                                    (-1, -1),
                                    5,
                                ),
                            ]
                        )
                    )

                    story.append(
                        table
                    )

                    story.append(
                        Spacer(
                            1,
                            8,
                        )
                    )

                index = next_index
                continue

            # ----------------------------------------------
            # Bullet
            # ----------------------------------------------

            if line.startswith("- "):

                bullet_text = (
                    line[2:].strip()
                )

                story.append(
                    Paragraph(
                        "• "
                        + self.clean_markdown(
                            bullet_text
                        ),
                        self.bullet_style,
                    )
                )

                index += 1
                continue

            # ----------------------------------------------
            # Normal paragraph
            # ----------------------------------------------

            story.append(
                Paragraph(
                    self.clean_markdown(
                        line
                    ),
                    self.body_style,
                )
            )

            index += 1

        document.build(
            story,

            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )

        return output_path