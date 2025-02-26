from datetime import datetime

from pydantic import BaseModel


class ServiceInfoResponseModel(BaseModel):
    info: str


class TelegramNotificationResponseModel(BaseModel):
    notification_method: str
    sent_message: str


class GmailNotificationResponseModel(BaseModel):
    notification_method: str
    to: str
    subject: str
    sent_message: str


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
    is_critical: bool
    is_extreme: bool
    base64_photo: str  # from Photo model (converted to base64 format)


class ConveyorParametersResponseModel(BaseModel):
    belt_length: int
    belt_width: int
    belt_thickness: int


class ConveyorStatusResponseModel(BaseModel):
    is_normal: bool
    is_extreme: bool
    is_critical: bool


class LogResponseModel(BaseModel):
    id: int
    timestamp: datetime  # from Object model
    type: str  # parameter "name" from LogType model
    text: str  # parameter "action" from Log model
