
import os
import re
import html

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
    HRFlowable,
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
            fontSize=21,
            leading=26,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#172554"),
            spaceAfter=14,
        )

        self.heading1_style = ParagraphStyle(
            "Heading1Custom",
            parent=self.styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        )

        self.heading2_style = ParagraphStyle(
            "Heading2Custom",
            parent=self.styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#334155"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        )

        self.body_style = ParagraphStyle(
            "BodyCustom",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#222222"),
            spaceAfter=6,
            splitLongWords=1,
        )

        self.bullet_style = ParagraphStyle(
            "BulletCustom",
            parent=self.body_style,
            leftIndent=14,
            firstLineIndent=-8,
            bulletIndent=3,
            spaceAfter=4,
        )

        self.small_style = ParagraphStyle(
            "SmallCustom",
            parent=self.styles["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            splitLongWords=1,
        )

        self.table_header_style = ParagraphStyle(
            "TableHeaderCustom",
            parent=self.small_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#172554"),
        )

    # ======================================================
    # MARKDOWN HELPERS
    # ======================================================

    def clean_markdown(self, text):

        if text is None:
            return ""

        text = str(text)

        # Escape XML-sensitive characters.
        text = html.escape(text, quote=False)

        # Inline code.
        text = re.sub(
            r"`(.+?)`",
            r"<font name='Courier'>\1</font>",
            text,
        )

        # Bold.
        text = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            text,
        )

        # Italic.
        text = re.sub(
            r"(?<!\*)\*([^*]+)\*(?!\*)",
            r"<i>\1</i>",
            text,
        )

        return text

    def parse_markdown_table(self, lines, start_index):

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

            # Detect Markdown separator row.
            is_separator = all(
                re.fullmatch(r":?-{3,}:?", cell.strip())
                for cell in cells
            )

            if not is_separator:
                rows.append(cells)

            index += 1

        return rows, index

    def normalize_table_rows(self, rows):

        if not rows:
            return []

        column_count = max(
            len(row)
            for row in rows
        )

        normalized = []

        for row in rows:

            row = list(row)

            while len(row) < column_count:
                row.append("")

            normalized.append(row)

        return normalized

    # ======================================================
    # TABLE GENERATION
    # ======================================================

    def create_table(self, rows):

        rows = self.normalize_table_rows(rows)

        if not rows:
            return None

        formatted_rows = []

        for row_index, row in enumerate(rows):

            formatted_row = []

            for cell in row:

                cleaned = self.clean_markdown(cell)

                style = (
                    self.table_header_style
                    if row_index == 0
                    else self.small_style
                )

                formatted_row.append(
                    Paragraph(
                        cleaned,
                        style
                    )
                )

            formatted_rows.append(
                formatted_row
            )

        column_count = len(formatted_rows[0])

        available_width = (
            A4[0] - (36 * mm)
        )

        # Equal column widths are a reasonable default.
        # Long text will wrap inside the cells.
        column_width = (
            available_width / column_count
        )

        table = Table(
            formatted_rows,
            colWidths=[
                column_width
            ] * column_count,
            repeatRows=1,
            hAlign="LEFT",
            splitByRow=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#E8EEF8"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#172554"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#CBD5E1"),
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

        return table

    # ======================================================
    # PAGE DECORATION
    # ======================================================

    def add_page_number(self, canvas, doc):

        canvas.saveState()

        width, height = A4

        # Footer line.
        canvas.setStrokeColor(
            colors.HexColor("#CBD5E1")
        )

        canvas.setLineWidth(0.5)

        canvas.line(
            18 * mm,
            15 * mm,
            width - 18 * mm,
            15 * mm,
        )

        # Footer text.
        canvas.setFont(
            "Helvetica",
            7.5,
        )

        canvas.setFillColor(
            colors.HexColor("#64748B")
        )

        canvas.drawString(
            18 * mm,
            10 * mm,
            "X ACCOUNT INVESTIGATOR",
        )

        canvas.drawRightString(
            width - 18 * mm,
            10 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    # ======================================================
    # MAIN PDF GENERATION
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
                exist_ok=True
            )

        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,

            rightMargin=18 * mm,
            leftMargin=18 * mm,

            topMargin=18 * mm,
            bottomMargin=21 * mm,

            title="X Account Investigation Report",
            author="X Account Investigator",

            allowSplitting=1,
        )

        story = []

        lines = report_text.splitlines()

        index = 0

        while index < len(lines):

            raw_line = lines[index]

            line = raw_line.strip()

            # --------------------------------------------------
            # Empty lines
            # --------------------------------------------------

            if not line:

                story.append(
                    Spacer(1, 3)
                )

                index += 1
                continue

            # --------------------------------------------------
            # Main title
            # --------------------------------------------------

            if line.startswith("# "):

                title = line[2:].strip()

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        self.clean_markdown(title),
                        self.title_style,
                    )
                )

                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=1,
                        color=colors.HexColor("#CBD5E1"),
                        spaceBefore=2,
                        spaceAfter=12,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Section heading
            # --------------------------------------------------

            if line.startswith("## "):

                heading = line[3:].strip()

                story.append(
                    Paragraph(
                        self.clean_markdown(heading),
                        self.heading1_style,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Subheading
            # --------------------------------------------------

            if line.startswith("### "):

                heading = line[4:].strip()

                story.append(
                    Paragraph(
                        self.clean_markdown(heading),
                        self.heading2_style,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Third-level heading
            # --------------------------------------------------

            if line.startswith("#### "):

                heading = line[5:].strip()

                story.append(
                    Paragraph(
                        self.clean_markdown(heading),
                        self.heading2_style,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Markdown table
            # --------------------------------------------------

            if line.startswith("|"):

                table_rows, next_index = (
                    self.parse_markdown_table(
                        lines,
                        index,
                    )
                )

                if table_rows:

                    table = self.create_table(
                        table_rows
                    )

                    if table:
                        story.append(table)

                        story.append(
                            Spacer(1, 8)
                        )

                index = next_index
                continue

            # --------------------------------------------------
            # Bullet
            # --------------------------------------------------

            if line.startswith("- "):

                bullet_text = line[2:].strip()

                story.append(
                    Paragraph(
                        "&#8226; "
                        + self.clean_markdown(
                            bullet_text
                        ),
                        self.bullet_style,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Numbered list
            # --------------------------------------------------

            numbered_match = re.match(
                r"^(\d+)\.\s+(.*)$",
                line
            )

            if numbered_match:

                number = numbered_match.group(1)
                content = numbered_match.group(2)

                story.append(
                    Paragraph(
                        f"<b>{number}.</b> "
                        + self.clean_markdown(content),
                        self.bullet_style,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Horizontal divider
            # --------------------------------------------------

            if line in ("---", "***", "___"):

                story.append(
                    HRFlowable(
                        width="100%",
                        thickness=0.5,
                        color=colors.HexColor("#CBD5E1"),
                        spaceBefore=5,
                        spaceAfter=8,
                    )
                )

                index += 1
                continue

            # --------------------------------------------------
            # Normal paragraph
            # --------------------------------------------------

            story.append(
                Paragraph(
                    self.clean_markdown(line),
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
