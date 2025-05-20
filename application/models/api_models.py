from datetime import datetime

from pydantic import BaseModel


class TelegramNotification(BaseModel):
    message: str


class GmailNotification(BaseModel):
    subject: str
    text: str


class ServiceInfoResponseModel(BaseModel):
    info: str


class MaintenanceActionResponseModel(BaseModel):
    maintenance_info: str


class TelegramNotificationResponseModel(BaseModel):
    notification_method: str
    to_user: str
    sent_message: str
    attached_file: str | None


class GmailNotificationResponseModel(BaseModel):
    notification_method: str
    to: str
    subject: str
    sent_text: str
    attached_file: str | None


class CountOfDefectGroupsResponseModel(BaseModel):
    total: int
    extreme: int
    critical: int


class DefectResponseModel(BaseModel):
    id: int
    timestamp: datetime  # from Object model
    type: str  # from DefectType model
    is_on_belt: bool  # from DefectType model
    box_width_in_mm: int
    box_length_in_mm: int
    longitudinal_position: int  # "location_length_in_conv" parameter
    transverse_position: int  # "location_width_in_conv" parameter
    probability: int
    criticality: str  # determined using parameters "is_critical" and "is_extreme"
    base64_photo: str  # from Photo model (converted to base64 format)


class TypesOfDefectsResponseModel(BaseModel):
    count: int
    types: list[str]


class NewConveyorParameters(BaseModel):
    new_belt_length: int
    new_belt_width: int
    new_belt_thickness: int


class ConveyorParametersResponseModel(BaseModel):
    belt_length: int
    belt_width: int
    belt_thickness: int


class ConveyorStatusResponseModel(BaseModel):
    status: str


class LogResponseModel(BaseModel):
    id: int
    timestamp: datetime  # from Object model
    type: str  # parameter "name" from LogType model
    text: str  # parameter "action" from Log model


class AllLogsRemovingResponseModel(BaseModel):
    status: str
    count_of_removed: int


class AllDefectsReportResponseModel(BaseModel):
    doc_type: str  # pdf / csv
    timestamp: datetime
    total_count: int
    extreme_count: int
    critical_count: int


class OneDefectReportResponseModel(BaseModel):
    doc_type: str  # pdf / csv
    timestamp: datetime
    defect: DefectResponseModel


class ConveyorInfoReportResponseModel(BaseModel):
    doc_type: str  # pdf / csv
    timestamp: datetime
    status: str  # normal / extreme / critical
