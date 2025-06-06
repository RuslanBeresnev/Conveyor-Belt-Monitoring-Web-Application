import base64
from datetime import datetime
from io import BytesIO
import binascii

import PIL

from fastapi import APIRouter, Depends, HTTPException
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, ListFlowable, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from application.user_settings import load_user_settings
from application.models.api_models import (ServiceInfoResponseModel, DefectResponseModel, AllDefectsReportResponseModel,
                                           OneDefectReportResponseModel, ConveyorInfoReportResponseModel)
from application.services.authentication_service import get_current_admin_user
from application.services.notification_service import (send_telegram_notification_from_server,
                                                       send_gmail_notification_from_server)
from application.services.defect_info_service import (get_count_of_all_and_extreme_and_critical_defects,
                                                      get_all_defects, get_defect_by_id, get_critical_defects,
                                                      get_extreme_defects)
from application.services.conveyor_info_service import get_base_conveyor_parameters, get_general_status_of_conveyor
from application.services.logging_service import create_log_record

router = APIRouter(prefix="/report", tags=["Reports Generation Service"],
                   dependencies=[Depends(get_current_admin_user)])


def format_defects_to_display_in_table(defects: list[DefectResponseModel], photo_size: (int, int)):
    """
    Parse array of json-defects into list of lists with values only.
    Also format timestamp value to readable format and replace base64-string with real photo in DefectResponseModel obj
    """
    table_values = [list(defect.model_dump().values()) for defect in defects]
    for defect_values in table_values:
        timestamp = datetime.fromisoformat(str(defect_values[1]))
        defect_values[1] = timestamp.strftime("%d.%m.%Y\n%H:%M:%S")
        base64_photo = defect_values[-1]
        image_raw_data = None
        try:
            image_raw_data = base64.b64decode(base64_photo)
        except (binascii.Error, TypeError) as e:
            error_type = "Decoding error"
            error_text = "incorrect base64-encoded representation of the photo"
            # Action logging
            create_log_record("error", "Failed to generate table of the defects in pdf-report: "
                                       f"{error_text}")
            raise HTTPException(status_code=500, detail=f"{error_type}: {error_text}") from e
        try:
            image_buffer = BytesIO(image_raw_data)
            image = Image(image_buffer, width=photo_size[0], height=photo_size[1])
        except (PIL.UnidentifiedImageError, TypeError) as e:
            error_type = "Unidentified image error"
            error_text = "raw representation of the photo is not bytes or has corrupted bytes sequence"
            # Action logging
            create_log_record("error", "Failed to generate table of the defects in pdf-report: "
                                       f"{error_text}")
            raise HTTPException(status_code=500, detail=f"{error_type}: {error_text}") from e
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

    for i, _ in enumerate(table_data):
        if table_data[i][9] == "extreme":
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.orange),
            ]))
        elif table_data[i][9] == "critical":
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.red),
            ]))


def convert_color_to_hex(color: Color):
    r = int(color.red * 255)
    g = int(color.green * 255)
    b = int(color.blue * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


async def send_report_as_notification(filename: str, caption: str):
    error_status_code, details = None, None

    # Sending generated report via Telegram
    if not load_user_settings() or "Telegram" in load_user_settings()["report_sending_scope"]:
        error_status_code, details = await send_telegram_notification_from_server(message=caption,
                                                                                  filename=filename)
    # Sending generated report via Gmail
    if not load_user_settings() or "Gmail" in load_user_settings()["report_sending_scope"]:
        error_status_code, details = send_gmail_notification_from_server(subject=caption, text="",
                                                                               filename=filename)

    return error_status_code, details


@router.get(path="/", response_model=ServiceInfoResponseModel)
def get_service_info():
    return ServiceInfoResponseModel(
        info="Service for generating reports on defects and conveyor status in .pdf or .csv format"
    )


@router.post(path="/all/pdf", response_model=AllDefectsReportResponseModel)
async def upload_report_of_all_defects_in_pdf_format():
    # pylint: disable=R0914
    filename = "report_of_all_defects.pdf"
    report_doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
    all_defects = get_all_defects()

    # Paragraph style for header text line break
    header_style = getSampleStyleSheet()["Normal"]
    table_headers = ["ID", "Timestamp", "Type", Paragraph("Is on belt", header_style),
                     Paragraph("Box width (mm)", header_style), Paragraph("Box length (mm)", header_style),
                     Paragraph("Longitudinal position (mm)", header_style),
                     Paragraph("Transverse position (mm)", header_style), "Probability", "Criticality", "Photo"]
    table_values = format_defects_to_display_in_table(all_defects, (133, 100))
    table_data = [table_headers] + table_values
    table = Table(table_data, colWidths=[20, 75, 75, 40, 75, 75, 75, 75, 50, 50, 133],
                  rowHeights=[30] + [100] * len(table_values))
    render_table_of_defects(table, table_data)

    title_style = getSampleStyleSheet()["Title"]
    title_style.fontSize = 24
    title_style.alignment = 1
    title_style.spaceAfter = 16
    title = Paragraph(f"REPORT ABOUT DEFECTS ({datetime.now().strftime("%d.%m.%Y - %H:%M")})", title_style)

    extreme_defects = get_extreme_defects()
    critical_defects = get_critical_defects()

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

    # Action logging
    create_log_record("report_info", "Report of the all defects in .pdf format has "
                                     "successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename,
                                                                   caption="PDF-report of all defects")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = AllDefectsReportResponseModel(
        doc_type="pdf",
        timestamp=datetime.now(),
        total_count=len(all_defects),
        extreme_count=len(extreme_defects),
        critical_count=len(critical_defects)
    )
    return response


@router.post(path="/id={defect_id}/pdf", response_model=OneDefectReportResponseModel)
async def upload_report_of_defect_by_id_in_pdf_format(defect_id: int):
    # pylint: disable=R0914
    filename = f"report_of_defect_id_{defect_id}.pdf"
    report_doc = SimpleDocTemplate(filename, pagesize=A4)
    try:
        defect = get_defect_by_id(defect_id)
    except HTTPException as e:
        # Action logging
        create_log_record("error", f"Failed to generate pdf-report of the defect with id={defect_id}: "
                                   f"{e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e

    # Paragraph style for header text line break
    header_style = getSampleStyleSheet()["Normal"]
    # Headers without photo!
    table_headers = ["ID", "Timestamp", "Type", Paragraph("Is on belt", header_style),
                     Paragraph("Box width (mm)", header_style), Paragraph("Box length (mm)", header_style),
                     Paragraph("Longitudinal pos. (mm)", header_style),
                     Paragraph("Transverse pos. (mm)", header_style), "Probability", "Criticality"]
    table_values = format_defects_to_display_in_table([defect], (575, 430))
    defect_photo = table_values[0].pop()
    table_data = [table_headers] + table_values
    table = Table(table_data, colWidths=[25, 75, 75, 40, 60, 60, 70, 70, 50, 50],
                  rowHeights=[30, 50])
    render_table_of_defects(table, table_data)

    title_style = getSampleStyleSheet()["Title"]
    title_style.fontSize = 24
    title_style.alignment = 1
    title_style.spaceAfter = 50
    title = Paragraph(f"REPORT ABOUT DEFECT WITH ID={defect_id} ({datetime.now().strftime("%d.%m.%Y - %H:%M")})",
                      title_style)

    elements = [title, table, Spacer(1, 25), defect_photo]
    report_doc.build(elements)

    # Action logging
    create_log_record("report_info", f"Report of the defect with id={defect_id} in .pdf format "
                                     "has successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename, caption=f"PDF-report of defect with "
                                                                                        f"id={defect_id}")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = OneDefectReportResponseModel(
        doc_type="pdf",
        timestamp=datetime.now(),
        defect=defect
    )
    return response


@router.post(path="/conveyor/pdf", response_model=ConveyorInfoReportResponseModel)
async def upload_report_of_conveyor_parameters_and_status_in_pdf_format():
    filename = "report_of_conveyor_info.pdf"
    report_doc = SimpleDocTemplate(filename, pagesize=A4)

    title_style = getSampleStyleSheet()["Title"]
    title_style.fontSize = 24
    title_style.alignment = 1
    title_style.spaceAfter = 32
    title = Paragraph(f"REPORT ABOUT CONVEYOR INFO ({datetime.now().strftime("%d.%m.%Y - %H:%M")})", title_style)

    parameters = get_base_conveyor_parameters()
    status_response = get_general_status_of_conveyor()
    status_text_color = None
    if status_response.status == "normal":
        status_text_color = colors.green
    elif status_response.status == "extreme":
        status_text_color = colors.orange
    elif status_response.status == "critical":
        status_text_color = colors.red

    defects_count = get_count_of_all_and_extreme_and_critical_defects()

    info_list_style = ParagraphStyle(
        name="InfoListStyle",
        parent=getSampleStyleSheet()["Normal"],
        fontSize=16,
        leading=20,
    )

    parameters_and_status = ListFlowable(
        [
            Paragraph(f"Belt length: <b>{parameters.belt_length / 1000000} km</b>", info_list_style),
            Paragraph(f"Belt width: <b>{parameters.belt_width / 1000} m</b>", info_list_style),
            Paragraph(f"Belt thickness: <b>{parameters.belt_thickness} mm</b>", info_list_style),
            Paragraph(f"General status: <b><font color=\"{convert_color_to_hex(status_text_color)}\">"
                      f"{status_response.status.upper()}</font></b>", info_list_style),
        ],
        bulletType="bullet"
    )

    defects_count_info = ListFlowable(
        [
            Paragraph(f"Total count of defects: <b>{defects_count.total}</b>", info_list_style),
            Paragraph(f"Count of extreme-level defects: <b>{defects_count.extreme}</b>", info_list_style),
            Paragraph(f"Count of critical-level defects: <b>{defects_count.critical}</b>", info_list_style)
        ],
        bulletType="bullet"
    )

    elements = [title, parameters_and_status, Spacer(1, 32), defects_count_info]
    report_doc.build(elements)

    # Action logging
    create_log_record("report_info", "Report of the conveyor parameters and status in .pdf format "
                                     "has successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename, caption="PDF-report of conveyor "
                                                                                        "parameters and status")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = ConveyorInfoReportResponseModel(
        doc_type="pdf",
        timestamp=datetime.now(),
        status=status_response.status
    )
    return response


@router.post(path="/all/csv", response_model=AllDefectsReportResponseModel)
async def upload_report_of_all_defects_in_csv_format():
    all_defects = get_all_defects()
    extreme_defects = get_extreme_defects()
    critical_defects = get_critical_defects()

    # Parameter "base64_photo" excluded from header and lines because base64-representation of defect's photo is large
    csv_table_headers = (",".join([str(key) for key in all_defects[0].model_dump().keys() if key != "base64_photo"]) +
                         "\n")
    csv_table_lines = [",".join([str(value) for key, value in defect.model_dump().items() if key != "base64_photo"]) +
                       "\n" for defect in all_defects]

    filename = "report_of_all_defects.csv"
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(csv_table_headers)
        output_file.writelines(line for line in csv_table_lines)

    # Action logging
    create_log_record("report_info", "Report of the all defects in .csv format "
                                     "has successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename, caption="CSV-report of all defects")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = AllDefectsReportResponseModel(
        doc_type="csv",
        timestamp=datetime.now(),
        total_count=len(all_defects),
        extreme_count=len(extreme_defects),
        critical_count=len(critical_defects)
    )
    return response


@router.post(path="/id={defect_id}/csv", response_model=OneDefectReportResponseModel)
async def upload_report_of_defect_by_id_in_csv_format(defect_id: int):
    try:
        defect = get_defect_by_id(defect_id)
    except HTTPException as e:
        # Action logging
        create_log_record("error", f"Failed to generate csv-report of the defect with id={defect_id}: "
                                   f"{e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e

    # Parameter "base64_photo" excluded from header and lines because base64-representation of defect's photo is large
    csv_headers = ",".join([str(key) for key in defect.model_dump().keys() if key != "base64_photo"]) + "\n"
    csv_defect_info = (",".join([str(value) for key, value in defect.model_dump().items() if key != "base64_photo"]) +
                       "\n")

    filename = f"report_of_defect_id_{defect_id}.csv"
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(csv_headers)
        output_file.write(csv_defect_info)

    # Action logging
    create_log_record("report_info", f"Report of the defect with id={defect_id} in .csv format "
                                     f"has successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename, caption=f"CSV-report of defect with "
                                                                                        f"id={defect_id}")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = OneDefectReportResponseModel(
        doc_type="csv",
        timestamp=datetime.now(),
        defect=defect
    )
    return response


@router.post(path="/conveyor/csv", response_model=ConveyorInfoReportResponseModel)
async def upload_report_of_conveyor_parameters_and_status_in_csv_format():
    parameters = get_base_conveyor_parameters()
    status_response = get_general_status_of_conveyor()
    defects_count = get_count_of_all_and_extreme_and_critical_defects()

    csv_headers = ("belt_length,belt_width,belt_thickness,general_status,total_count_of_defects,count_of_extreme,"
                   "count_of_critical\n")
    csv_conveyor_info = (",".join([str(value) for value in parameters.model_dump().values()]) +
                         f",{status_response.status}," +
                         ",".join([str(value) for value in defects_count.model_dump().values()]) + "\n")

    filename = "report_of_conveyor_info.csv"
    with open("report_of_conveyor_info.csv", "w", encoding="utf-8") as output_file:
        output_file.write(csv_headers)
        output_file.write(csv_conveyor_info)

    # Action logging
    create_log_record("report_info", "Report of the conveyor parameters and status in .csv format "
                                     "has successfully generated")

    # Report sending via Telegram and Gmail
    error_status_code, details = await send_report_as_notification(filename=filename, caption="CSV-report of conveyor "
                                                                                        "parameters and status")
    if error_status_code:
        raise HTTPException(status_code=error_status_code, detail="Report was successfully generated, but there was "
                                                                  f"error during notification sending: {details}")

    response = ConveyorInfoReportResponseModel(
        doc_type="csv",
        timestamp=datetime.now(),
        status=status_response.status
    )
    return response
