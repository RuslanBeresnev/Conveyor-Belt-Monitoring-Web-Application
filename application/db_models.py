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
    time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))

    type_object: ObjectType = Relationship(back_populates="objects")
    defect: list["Defect"] = Relationship(sa_relationship_kwargs={"uselist": False}, back_populates="base_object",
                                          cascade_delete=True)
    photo: list["Photo"] = Relationship(sa_relationship_kwargs={"uselist": False}, back_populates="base_object",
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
