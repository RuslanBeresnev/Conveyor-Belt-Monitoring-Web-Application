from pydantic import BaseModel
from datetime import datetime


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
