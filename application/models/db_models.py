from datetime import datetime

from sqlmodel import SQLModel, Field, Column, Relationship, Integer, TEXT, DateTime, LargeBinary


class ObjectType(SQLModel, table=True):
    __tablename__ = "object_type"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    name: str = Field(sa_column=Column(TEXT, nullable=False))

    objects: list["Object"] = Relationship(back_populates="type_object", cascade_delete=True)


class Object(SQLModel, table=True):
    __tablename__ = "objects"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    type: int = Field(foreign_key="object_type.id", nullable=False, ondelete="CASCADE")
    time: datetime = Field(sa_column=Column(DateTime(timezone=False)))

    type_object: ObjectType = Relationship(back_populates="objects")

    # 1:1 relation
    defect: "Defect" = Relationship(sa_relationship_kwargs=dict(uselist=False), back_populates="base_object",
                                    cascade_delete=True)
    # 1:1 relation
    photo: "Photo" = Relationship(sa_relationship_kwargs=dict(uselist=False), back_populates="base_object",
                                  cascade_delete=True)
    # 1:1 relation
    conveyor_status: "ConveyorStatus" = Relationship(sa_relationship_kwargs=dict(uselist=False),
                                                     back_populates="base_object", cascade_delete=True)
    # 1:1 relation
    log: "Log" = Relationship(sa_relationship_kwargs=dict(uselist=False), back_populates="base_object",
                              cascade_delete=True)


class DefectType(SQLModel, table=True):
    __tablename__ = "defect_type"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    name: str = Field(sa_column=Column(TEXT, nullable=False))
    is_belt: bool = Field(default=True, nullable=False)
    width_critical: int = Field(default=500, nullable=False)
    length_critical: int = Field(default=500, nullable=False)
    location_width_shift: int = Field(default=50, nullable=False)
    location_length_shift: int = Field(default=500, nullable=False)
    time_for_comparison: int = Field(default=30, nullable=False)
    width_extreme: int = Field(default=400, nullable=False)
    length_extreme: int = Field(default=400, nullable=False)

    defects: list["Defect"] = Relationship(back_populates="type_object", cascade_delete=True)


class Photo(SQLModel, table=True):
    __tablename__ = "photo"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    obj_id: int = Field(foreign_key="objects.id", nullable=False, ondelete="CASCADE")
    image: bytes = Field(sa_column=Column(LargeBinary, nullable=False))

    base_object: Object = Relationship(back_populates="photo")
    defects: list["Defect"] = Relationship(back_populates="photo_object", cascade_delete=True)


class Defect(SQLModel, table=True):
    __tablename__ = "defects"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    obj_id: int = Field(foreign_key="objects.id", nullable=False, ondelete="CASCADE")
    type: int = Field(foreign_key="defect_type.id", nullable=False, ondelete="CASCADE")
    box_width: int = Field(nullable=False)
    box_length: int = Field(nullable=False)
    location_width_in_frame: int = Field(nullable=False)
    location_length_in_frame: int = Field(nullable=False)
    location_width_in_conv: int = Field(nullable=False)
    location_length_in_conv: int = Field(nullable=False)
    photo_id: int = Field(foreign_key="photo.id", nullable=False, ondelete="CASCADE")
    probability: int = Field(nullable=False)
    is_critical: bool = Field(default=False, nullable=False)
    is_extreme: bool = Field(default=False, nullable=False)

    base_object: Object = Relationship(back_populates="defect")
    type_object: DefectType = Relationship(back_populates="defects")
    photo_object: Photo = Relationship(back_populates="defects")

    # Link to the object of this defect in Relation table (1:1 relation)
    current_defect_in_relation: "Relation" = (
        Relationship(sa_relationship_kwargs=dict(uselist=False, foreign_keys="[Relation.id_current]"),
                     back_populates="current_defect_object", cascade_delete=True))
    # Link to the object of previous defect for this in Relation table (1:1 relation)
    previous_defect_in_relation: "Relation" = (
        Relationship(sa_relationship_kwargs=dict(uselist=False, foreign_keys="[Relation.id_previous]"),
                     back_populates="previous_defect_object", cascade_delete=True))


class Relation(SQLModel, table=True):
    """
    This table implements the chain of variations for the one defect
    (essentially a singly linked list for observing defect progression)
    """
    __tablename__ = "relation"
    id_current: int = Field(foreign_key="defects.id", primary_key=True, nullable=False, ondelete="CASCADE")
    id_previous: int = Field(foreign_key="defects.id", primary_key=True, nullable=False, ondelete="CASCADE")

    current_defect_object: Defect = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Relation.id_current]"),
                                                 back_populates="current_defect_in_relation")
    previous_defect_object: Defect = Relationship(sa_relationship_kwargs=dict(foreign_keys="[Relation.id_previous]"),
                                                  back_populates="previous_defect_in_relation")


class ConveyorParameters(SQLModel, table=True):
    __tablename__ = "conv"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    belt_length: int = Field(default=17360000, nullable=False)
    belt_width: int = Field(default=3360, nullable=False)
    belt_thickness: int = Field(default=15, nullable=False)


class ConveyorStatus(SQLModel, table=True):
    __tablename__ = "state_of_conv"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    id_obj: int = Field(foreign_key="objects.id", nullable=False, ondelete="CASCADE")
    is_critical: bool = Field(default=False, nullable=False)
    is_extreme: bool = Field(default=False, nullable=False)

    base_object: Object = Relationship(back_populates="conveyor_status")


class LogType(SQLModel, table=True):
    __tablename__ = "history_type"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    name: str = Field(nullable=False)

    logs: list["Log"] = Relationship(back_populates="type_object", cascade_delete=True)


class Log(SQLModel, table=True):
    __tablename__ = "history"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    id_obj: int = Field(foreign_key="objects.id", nullable=False, ondelete="CASCADE")
    action: str = Field(nullable=False)
    type: int = Field(foreign_key="history_type.id", nullable=False, ondelete="CASCADE")

    base_object: Object = Relationship(back_populates="log")
    type_object: LogType = Relationship(back_populates="logs")


class Version(SQLModel, table=True):
    __tablename__ = "version"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    version: str = Field(default="1.0.2", nullable=False)


class CameraSettings(SQLModel, table=True):
    __tablename__ = "camera_settings"
    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False, autoincrement=True))
    mm_pix: int = Field(nullable=False)
