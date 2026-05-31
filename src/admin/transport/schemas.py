from typing import Optional

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel


# --- Transport Stats ---


class TransportStatsResponse(BaseModel):
    total_vehicles: int
    operational_vehicles: int
    under_maintenance: int
    out_of_order: int
    total_drivers: int
    active_drivers: int
    available_drivers: int
    total_helpers: int
    active_routes: int
    total_assignments: int
    total_students_transported: int


# --- Vehicle Schemas ---


class VehicleCreateRequest(BaseModel):
    vehicle_number: str
    plate_number: str | None = None
    type: str
    model: str | None = None
    year: int | None = None
    fuel_type: str | None = None
    capacity: int
    status: str = "Operational"
    next_service_date: date | None = None
    insurance_expiry: date | None = None
    fitness_expiry: date | None = None


class VehicleUpdateRequest(BaseModel):
    vehicle_number: str | None = None
    plate_number: str | None = None
    type: str | None = None
    model: str | None = None
    year: int | None = None
    fuel_type: str | None = None
    capacity: int | None = None
    status: str | None = None
    next_service_date: date | None = None
    insurance_expiry: date | None = None
    fitness_expiry: date | None = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    vehicle_number: str
    plate_number: str | None = None
    type: str
    model: str | None = None
    year: int | None = None
    fuel_type: str | None = None
    capacity: int
    occupied_seats: int = 0
    status: str
    driver_id: uuid.UUID | None = None
    driver_name: str | None = None
    route_id: uuid.UUID | None = None
    route_name: str | None = None
    next_service_date: date | None = None
    insurance_expiry: date | None = None
    fitness_expiry: date | None = None
    is_active: bool
    created_at: datetime | None = None
    metadata: dict = {}


class VehicleListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[VehicleResponse]


class VehicleDeleteResponse(BaseModel):
    id: uuid.UUID
    vehicle_number: str
    status: str
    deactivated_on: str
    message: str


# --- Driver Schemas ---


class DriverCreateRequest(BaseModel):
    full_name: str
    phone: str
    email: str | None = None
    license_number: str
    license_type: str | None = None
    license_expiry: date | None = None
    experience_years: int | None = None
    join_date: date | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class DriverUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    license_number: str | None = None
    license_type: str | None = None
    license_expiry: date | None = None
    experience_years: int | None = None
    join_date: date | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


class DriverResponse(BaseModel):
    id: uuid.UUID
    driver_id: str
    full_name: str
    phone: str
    email: str | None = None
    license_number: str
    license_type: str | None = None
    license_expiry: date | None = None
    experience_years: int | None = None
    join_date: date | None = None
    status: str
    assigned_vehicle_id: uuid.UUID | None = None
    assigned_vehicle: str | None = None
    assigned_route: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    is_active: bool
    created_at: datetime | None = None
    metadata: dict = {}


class DriverListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[DriverResponse]


class DriverDeleteResponse(BaseModel):
    id: uuid.UUID
    driver_id: str
    full_name: str
    status: str
    deactivated_on: str
    message: str


# --- Helper Schemas ---


class HelperCreateRequest(BaseModel):
    full_name: str
    phone: str
    join_date: date | None = None


class HelperUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    join_date: date | None = None


class HelperResponse(BaseModel):
    id: uuid.UUID
    helper_id: str
    full_name: str
    phone: str
    join_date: date | None = None
    status: str
    assigned_vehicle_id: uuid.UUID | None = None
    assigned_vehicle: str | None = None
    assigned_route: str | None = None
    is_active: bool
    created_at: datetime | None = None
    metadata: dict = {}


class HelperListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[HelperResponse]


class HelperDeleteResponse(BaseModel):
    id: uuid.UUID
    helper_id: str
    full_name: str
    status: str
    deactivated_on: str
    message: str


# --- Route Schemas ---


class RouteCreateRequest(BaseModel):
    name: str
    area: str | None = None
    shift: str | None = None
    stops: int | dict | list | None = None
    distance_km: float | None = None
    start_time: time | None = None
    end_time: time | None = None


class RouteUpdateRequest(BaseModel):
    name: str | None = None
    area: str | None = None
    shift: str | None = None
    stops: int | dict | list | None = None
    distance_km: float | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: str | None = None


class RouteResponse(BaseModel):
    id: uuid.UUID
    route_code: str
    name: str
    area: str | None = None
    shift: str | None = None
    stops: int | dict | list | None = None
    distance_km: float | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: str
    assigned_vehicle: str | None = None
    assigned_driver: str | None = None
    students_count: int = 0
    is_active: bool
    created_at: datetime | None = None
    metadata: dict = {}


class RouteListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[RouteResponse]


class RouteDeleteResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    deactivated_on: str
    message: str


# --- Assignment Schemas ---


class AssignmentCreateRequest(BaseModel):
    route_id: uuid.UUID
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    helper_id: uuid.UUID | None = None


class AssignmentUpdateRequest(BaseModel):
    route_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    helper_id: uuid.UUID | None = None


class AssignmentResponse(BaseModel):
    id: uuid.UUID
    route_id: uuid.UUID
    route_name: str
    route_code: str | None = None
    area: str | None = None
    shift: str | None = None
    stops: int | dict | list | None = None
    distance_km: float | None = None
    start_time: time | None = None
    end_time: time | None = None
    vehicle_id: uuid.UUID
    vehicle_number: str
    vehicle_type: str | None = None
    vehicle_capacity: int | None = None
    occupied_seats: int | None = None
    driver_id: uuid.UUID
    driver_name: str
    driver_phone: str | None = None
    helper_id: uuid.UUID | None = None
    helper_name: str | None = None
    helper_phone: str | None = None
    status: str
    is_active: bool
    created_at: datetime | None = None
    metadata: dict = {}


class AssignmentListResponse(BaseModel):
    count: int
    page: int
    page_size: int
    total_pages: int
    results: list[AssignmentResponse]


class AssignmentDeleteResponse(BaseModel):
    id: uuid.UUID
    route_name: str
    status: str
    deactivated_on: str
    message: str
