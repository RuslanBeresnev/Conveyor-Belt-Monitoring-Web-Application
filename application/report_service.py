import base64
from datetime import datetime
from io import BytesIO

import requests

from fastapi import APIRouter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, ListFlowable, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .response_models import ServiceInfoResponseModel, DefectResponseModel, AllDefectsReportResponseModel

router = APIRouter(prefix="/report", tags=["Reports Generation Service"])


def format_defects_to_display_in_table(defects: list[DefectResponseModel]):
    """
    Parse array of json-defects into list of lists with values only.
    Also format timestamp value to readable format and replace base64-string with real photo in DefectResponseModel obj
    """
    table_values = [[value for key, value in defect.items()] for defect in defects]
    for defect_values in table_values:
        timestamp = datetime.fromisoformat(defect_values[1])
        defect_values[1] = timestamp.strftime("%d.%m.%Y\n%H:%M:%S")
        base64_photo = defect_values[-1]
        image_raw_data = base64.b64decode(base64_photo)
        image_buffer = BytesIO(image_raw_data)
        image = Image(image_buffer, width=133, height=100)
        defect_values[-1] = image
    return table_values


def render_table_of_defects(table: Table, table_data: list):
    """
    Render base table style using TableStyle object.
    Also apply TableStyle object to table lines with extreme and critical defects
    """
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    for i in range(len(table_data)):
        if table_data[i][-2] == "extreme":
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.orange),
            ]))
        elif table_data[i][-2] == "critical":
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.red),
            ]))


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service for generating reports on defects and conveyor status in .pdf or .csv format"
    )


@router.post(path="/all/pdf", response_model=AllDefectsReportResponseModel)
def upload_report_of_all_defects_in_pdf_format():
    report_doc = SimpleDocTemplate("report_of_all_defects.pdf", pagesize=landscape(A4))
    all_defects = requests.get("http://127.0.0.1:8000/defect_info/all").json()

    # Paragraph style for header text line break
    header_style = getSampleStyleSheet()["Normal"]
    table_headers = ["ID", "Timestamp", "Type", Paragraph("Is on belt", header_style),
                     Paragraph("Box width (mm)", header_style), Paragraph("Box length (mm)", header_style),
                     Paragraph("Longitudinal position (mm)", header_style),
                     Paragraph("Transverse position (mm)", header_style), "Probability", "Criticality", "Photo"]
    table_values = format_defects_to_display_in_table(all_defects)
    table_data = [table_headers] + table_values
    table = Table(table_data, colWidths=[20, 75, 75, 40, 75, 75, 75, 75, 50, 50, 133],
                  rowHeights=[30] + [100] * len(table_values))
    render_table_of_defects(table, table_data)

    title_style = getSampleStyleSheet()["Title"]
    title_style.fontSize = 24
    title_style.alignment = 1
    title_style.spaceAfter = 16
    title = Paragraph(f"REPORT ABOUT DEFECTS ({datetime.now().strftime("%d.%m.%Y - %H:%M")})", title_style)

    extreme_defects = requests.get("http://127.0.0.1:8000/defect_info/extreme").json()
    critical_defects = requests.get("http://127.0.0.1:8000/defect_info/critical").json()

    statistics_style = getSampleStyleSheet()["Normal"]
    general_statistics = ListFlowable(
        [
            Paragraph(f"Total count of defects: {len(all_defects)}", statistics_style),
            Paragraph(f"Count of extreme: {len(extreme_defects)}", statistics_style),
            Paragraph(f"Count of critical: {len(critical_defects)}", statistics_style),
        ],
        bulletType="bullet"
    )

    elements = [title, general_statistics, Spacer(1, 25), table]
    report_doc.build(elements)

    response = AllDefectsReportResponseModel(
        doc_type="pdf",
        timestamp=datetime.now(),
        total_count=len(all_defects),
        extreme_count=len(extreme_defects),
        critical_count=len(critical_defects)
    )
    return response
