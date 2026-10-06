from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

import analysis


BASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = BASE_DIR / "plots"
REPORTS_DIR = BASE_DIR / "reports"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=15
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            alignment=TA_LEFT,
            spaceAfter=7
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11
        )
    )

    return styles


def format_value(value, decimals=4):
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def build_summary_table(summary):
    rows = [
        ["Parameter", "Result"]
    ]

    for parameter, value in summary.items():

        if parameter == "BET surface area":
            result = (
                f"{format_value(value)} m²/g"
            )

        elif parameter == "BJH mode pore radius":
            result = (
                f"{format_value(value)} nm"
            )

        elif parameter == "BJH cumulative pore volume":
            result = (
                f"{format_value(value)} cm³/g"
            )

        elif parameter == "DFT peak pore width":
            result = (
                f"{format_value(value)} nm"
            )

        elif parameter == "XRD peak position":
            result = (
                f"{format_value(value)}°"
            )

        elif parameter == "XRD peak intensity":
            result = (
                f"{format_value(value, 0)} counts"
            )

        elif parameter == "EDS element count":
            result = str(value)

        elif parameter == "SEM image count":
            result = str(value)

        else:
            result = str(value)

        rows.append([parameter, result])

    table = Table(
        rows,
        colWidths=[
            9 * cm,
            7 * cm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f4e78")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f2f5f7")
                ]
            )
        ])
    )

    return table


def build_eds_table():
    data = analysis.load_eds()

    rows = [
        [
            "Element",
            "Weight (%)",
            "Sigma"
        ]
    ]

    for row in data:
        rows.append([
            row["element"],
            format_value(
                row["weight_percent"],
                2
            ),
            format_value(
                row["sigma"],
                2
            )
        ])

    table = Table(
        rows,
        colWidths=[
            5 * cm,
            5 * cm,
            5 * cm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f4e78")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "CENTER"
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f2f5f7")
                ]
            )
        ])
    )

    return table


def add_plot(story, filename, title, width=16):
    path = PLOTS_DIR / filename

    if not path.exists():
        return

    story.append(
        Paragraph(
            title,
            create_styles()["SectionTitle"]
        )
    )

    image = Image(
        str(path),
        width=width * cm,
        height=width * 0.60 * cm
    )

    story.append(image)
    story.append(Spacer(1, 0.3 * cm))


def build_report(output_path=None):
    styles = create_styles()

    if output_path is None:
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_path = (
            REPORTS_DIR /
            f"MWCNT_Characterization_Report_{timestamp}.pdf"
        )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "MULTI-WALLED CARBON NANOTUBE",
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Characterization Analysis Report",
            styles["ReportTitle"]
        )
    )

    story.append(Spacer(1, 0.4 * cm))

    date_text = datetime.now().strftime(
        "%d %B %Y"
    )

    story.append(
        Paragraph(
            f"Report generated: {date_text}",
            styles["BodyTextCustom"]
        )
    )

    story.append(Spacer(1, 0.5 * cm))

    story.append(
        Paragraph(
            "This report presents the analysis of the available "
            "multi-walled carbon nanotube characterization data. "
            "The analysis uses the processed experimental datasets "
            "available in the project data directory.",
            styles["BodyTextCustom"]
        )
    )

    # -----------------------------------------------------
    # CHARACTERIZATION SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "1. Characterization Summary",
            styles["SectionTitle"]
        )
    )

    summary = analysis.get_characterization_summary()

    story.append(
        build_summary_table(summary)
    )

    story.append(Spacer(1, 0.5 * cm))

    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "2. General Evaluation",
            styles["SectionTitle"]
        )
    )

    observations = analysis.evaluate_characterization()

    for observation in observations:
        story.append(
            Paragraph(
                f"• {observation}",
                styles["BodyTextCustom"]
            )
        )

    # -----------------------------------------------------
    # BET
    # -----------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "3. BET Surface Area and Isotherm Analysis",
            styles["SectionTitle"]
        )
    )

    bet_area = analysis.get_bet_surface_area()

    story.append(
        Paragraph(
            f"The extracted BET dataset reports a specific "
            f"surface area of {format_value(bet_area)} m²/g. "
            f"The adsorption data were used to generate the "
            f"available isotherm plot.",
            styles["BodyTextCustom"]
        )
    )

    add_plot(
        story,
        "bet_isotherm.png",
        "BET Adsorption-Desorption Isotherm"
    )

    # -----------------------------------------------------
    # BJH
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "4. BJH Pore Size Distribution",
            styles["SectionTitle"]
        )
    )

    bjh_radius = analysis.get_bjh_mode_radius()
    bjh_volume = analysis.get_bjh_total_pore_volume()

    story.append(
        Paragraph(
            f"The calculated mode of the BJH adsorption pore "
            f"radius distribution is {format_value(bjh_radius)} nm. "
            f"The maximum cumulative pore volume represented in "
            f"the extracted adsorption dataset is "
            f"{format_value(bjh_volume)} cm³/g.",
            styles["BodyTextCustom"]
        )
    )

    add_plot(
        story,
        "bjh_comparison.png",
        "BJH Adsorption and Desorption Comparison"
    )

    # -----------------------------------------------------
    # DFT
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "5. DFT Pore Structure Analysis",
            styles["SectionTitle"]
        )
    )

    dft_peak = analysis.get_dft_peak_pore_width()

    story.append(
        Paragraph(
            f"The DFT pore-size dataset indicates a maximum "
            f"differential pore-volume response at approximately "
            f"{format_value(dft_peak)} nm within the available "
            f"dataset.",
            styles["BodyTextCustom"]
        )
    )

    add_plot(
        story,
        "dft_distribution.png",
        "DFT Pore Size Distribution"
    )

    add_plot(
        story,
        "dft_surface_area.png",
        "DFT Surface Area Distribution"
    )

    add_plot(
        story,
        "dft_fitting.png",
        "DFT Model Fitting"
    )

    # -----------------------------------------------------
    # EDS
    # -----------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "6. EDS Elemental Composition",
            styles["SectionTitle"]
        )
    )

    eds_total = analysis.get_eds_total()

    story.append(
        Paragraph(
            f"The EDS dataset contains "
            f"{len(analysis.load_eds())} reported elements. "
            f"The sum of the reported weight percentages is "
            f"{format_value(eds_total, 2)}%.",
            styles["BodyTextCustom"]
        )
    )

    story.append(
        build_eds_table()
    )

    story.append(Spacer(1, 0.4 * cm))

    add_plot(
        story,
        "eds_composition.png",
        "EDS Elemental Composition"
    )

    # -----------------------------------------------------
    # XRD
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "7. X-Ray Diffraction Analysis",
            styles["SectionTitle"]
        )
    )

    xrd_peak = analysis.get_xrd_peak()

    if xrd_peak:
        story.append(
            Paragraph(
                f"The highest intensity point in the supplied "
                f"XRD pattern occurs at approximately "
                f"{format_value(xrd_peak['two_theta'])}° "
                f"2θ, with an intensity of "
                f"{format_value(xrd_peak['intensity'], 0)} counts.",
                styles["BodyTextCustom"]
            )
        )

    add_plot(
        story,
        "xrd_pattern.png",
        "X-Ray Diffraction Pattern"
    )

    # -----------------------------------------------------
    # SEM
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "8. SEM and Morphological Data",
            styles["SectionTitle"]
        )
    )

    sem_count = analysis.get_sem_image_count()

    story.append(
        Paragraph(
            f"The project contains {sem_count} SEM image records "
            f"with associated metadata. The available images can "
            f"be examined separately for morphological "
            f"interpretation. Quantitative dimensions should only "
            f"be reported when they are directly measured from "
            f"the image scale.",
            styles["BodyTextCustom"]
        )
    )

    # -----------------------------------------------------
    # CONCLUSION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "9. Conclusion",
            styles["SectionTitle"]
        )
    )

    story.append(
        Paragraph(
            "The characterization dataset provides complementary "
            "information concerning the surface area, pore "
            "structure, elemental composition, crystal-related "
            "diffraction features, and available morphology data "
            "of the MWCNT sample. BET, BJH and DFT analyses provide "
            "surface and pore-structure information, while EDS and "
            "XRD provide compositional and structural information. "
            "SEM data provide the basis for morphological "
            "examination.",
            styles["BodyTextCustom"]
        )
    )

    story.append(
        Paragraph(
            "The numerical values presented in this report are "
            "derived from the processed datasets available to the "
            "application. Further scientific interpretation should "
            "be made alongside the original experimental conditions "
            "and instrument reports.",
            styles["BodyTextCustom"]
        )
    )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(story)

    return Path(output_path)


def generate_report():
    return build_report()


if __name__ == "__main__":
    report = generate_report()

    print()
    print("MWCNT report generated successfully.")
    print(f"Report: {report}")