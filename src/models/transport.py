from __future__ import annotations

import uuid
from datetime import date, time

from sqlalchemy import ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel, UUIDType


class Vehicle(BaseModel):
    """Vehicle inventory for the transport fleet."""

    __tablename__ = "vehicles"

    vehicle_number: Mapped[str] = mapped_column(String(50), nullable=False)
    plate_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # Bus/Van/Mini-Bus
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year: Mapped[int | None] = mapped_column(nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    capacity: Mapped[int] = mapped_column(nullable=False)
    occupied_seats: Mapped[int] = mapped_column(default=0, server_default="0")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Operational", server_default="Operational"
    )  # Operational/Maintenance/Out-Of-Order
    next_service_date: Mapped[date | None] = mapped_column(nullable=True)
    insurance_expiry: Mapped[date | None] = mapped_column(nullable=True)
    fitness_expiry: Mapped[date | None] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("school_id", "vehicle_number", name="uq_vehicles_school_vehicle_number"),
        Index("idx_vehicles_status", "school_id", "status"),
    )


class Driver(BaseModel):
    """Driver records for the transport fleet."""

    __tablename__ = "drivers"

    driver_id: Mapped[str] = mapped_column(String(50), nullable=False)  # DRV001
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    license_number: Mapped[str] = mapped_column(String(50), nullable=False)
    license_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # Heavy Vehicle/Light Vehicle
    license_expiry: Mapped[date | None] = mapped_column(nullable=True)
    experience_years: Mapped[int | None] = mapped_column(nullable=True)
    join_date: Mapped[date | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Available", server_default="Available"
    )  # Active/Available/Inactive
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    __table_args__ = (
        UniqueConstraint("school_id", "driver_id", name="uq_drivers_school_driver_id"),
        Index("idx_drivers_status", "school_id", "status"),
    )


class Helper(BaseModel):
    """Helper/attendant records for the transport fleet."""

    __tablename__ = "helpers"

    helper_id: Mapped[str] = mapped_column(String(50), nullable=False)  # HLP001
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    join_date: Mapped[date | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Available", server_default="Available"
    )  # Active/Available/Inactive

    __table_args__ = (
        UniqueConstraint("school_id", "helper_id", name="uq_helpers_school_helper_id"),
        Index("idx_helpers_status", "school_id", "status"),
    )


class Route(BaseModel):
    """Transport routes."""

    __tablename__ = "routes"

    route_code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shift: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Morning/Afternoon/Evening
    stops: Mapped[dict] = mapped_column(JSON, default=list)
    distance_km: Mapped[float | None] = mapped_column(nullable=True)
    start_time: Mapped[time | None] = mapped_column(nullable=True)
    end_time: Mapped[time | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Active", server_default="Active"
    )  # Active/Inactive

    __table_args__ = (
        UniqueConstraint("school_id", "route_code", name="uq_routes_school_route_code"),
        Index("idx_routes_status", "school_id", "status"),
    )


class RouteAssignment(BaseModel):
    """Operational mapping: route + vehicle + driver + helper."""

    __tablename__ = "route_assignments"

    route_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("routes.id"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("vehicles.id"), nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("drivers.id"), nullable=False
    )
    helper_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("helpers.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Active", server_default="Active"
    )  # Active/Inactive

    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "vehicle_id",
            name="uq_route_assignments_school_vehicle",
        ),
        Index("idx_route_assignments_route", "route_id"),
        Index("idx_route_assignments_vehicle", "vehicle_id"),
        Index("idx_route_assignments_driver", "driver_id"),
    )


class StudentTransport(BaseModel):
    """Maps student to a route + pickup/drop point per academic year."""

    __tablename__ = "student_transport"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("students.id"), nullable=False
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("routes.id"), nullable=False
    )
    academic_year_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("academic_years.id"), nullable=False
    )
    pickup_point: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drop_point: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "student_id",
            "academic_year_id",
            name="uq_student_transport_school_student_year",
        ),
        Index("idx_student_transport_route", "route_id", "academic_year_id"),
        Index("idx_student_transport_student", "student_id"),
    )
