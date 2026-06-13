from __future__ import annotations

import csv
import io
import uuid

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.admin.transport import service
from src.admin.transport.schemas import (
    AssignmentCreateRequest,
    AssignmentDeleteResponse,
    AssignmentListResponse,
    AssignmentResponse,
    AssignmentUpdateRequest,
    DriverCreateRequest,
    DriverDeleteResponse,
    DriverListResponse,
    DriverResponse,
    DriverUpdateRequest,
    HelperCreateRequest,
    HelperDeleteResponse,
    HelperListResponse,
    HelperResponse,
    HelperUpdateRequest,
    RouteCreateRequest,
    RouteDeleteResponse,
    RouteListResponse,
    RouteResponse,
    RouteUpdateRequest,
    TransportStatsResponse,
    VehicleCreateRequest,
    VehicleDeleteResponse,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdateRequest,
)
from src.auth.dependencies import AdminUser, SchoolDep
from src.core.dependencies import PaginationDep, SessionDep

router = APIRouter(prefix="/admin/transport", tags=["Admin Transport"])


# ────────────────────────────────────────────────────────────────────────────────
# Stats
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/stats", response_model=TransportStatsResponse)
async def get_transport_stats(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> TransportStatsResponse:
    """Get transport KPI summary."""
    result = await service.get_transport_stats(db, school.id)
    return TransportStatsResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Vehicles
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/vehicles/export")
async def export_vehicles(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StreamingResponse:
    """Export vehicles as CSV."""
    rows = await service.export_vehicles(db, school.id)

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        writer = csv.writer(output)
        writer.writerow([
            "vehicle_number", "plate_number", "type", "model", "year",
            "fuel_type", "capacity", "occupied_seats", "status",
            "next_service_date", "insurance_expiry", "fitness_expiry",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vehicles.csv"},
    )


@router.get("/vehicles", response_model=VehicleListResponse)
async def list_vehicles(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> VehicleListResponse:
    """List all vehicles with optional filters."""
    result = await service.list_vehicles(db, school.id, pagination, search, type, status)
    return VehicleListResponse(**result)


@router.post("/vehicles", status_code=201, response_model=VehicleResponse)
async def create_vehicle(
    data: VehicleCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> VehicleResponse:
    """Add a new vehicle."""
    result = await service.create_vehicle(db, school.id, data.model_dump(), user.id)
    return VehicleResponse(**result)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> VehicleResponse:
    """Get vehicle details."""
    result = await service.get_vehicle(db, school.id, vehicle_id)
    return VehicleResponse(**result)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    data: VehicleUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> VehicleResponse:
    """Update vehicle details."""
    result = await service.update_vehicle(
        db, school.id, vehicle_id, data.model_dump(exclude_unset=True), user.id
    )
    return VehicleResponse(**result)


@router.delete("/vehicles/{vehicle_id}", response_model=VehicleDeleteResponse)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> VehicleDeleteResponse:
    """Soft-delete a vehicle."""
    result = await service.delete_vehicle(db, school.id, vehicle_id, user.id)
    return VehicleDeleteResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Drivers
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/drivers/export")
async def export_drivers(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> StreamingResponse:
    """Export drivers as CSV."""
    rows = await service.export_drivers(db, school.id)

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        writer = csv.writer(output)
        writer.writerow([
            "driver_id", "full_name", "phone", "email", "license_number",
            "license_type", "license_expiry", "experience_years", "join_date",
            "status", "emergency_contact_name", "emergency_contact_phone",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=drivers.csv"},
    )


@router.get("/drivers", response_model=DriverListResponse)
async def list_drivers(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    license_type: str | None = Query(default=None),
) -> DriverListResponse:
    """List all drivers with optional filters."""
    result = await service.list_drivers(db, school.id, pagination, search, status, license_type)
    return DriverListResponse(**result)


@router.post("/drivers", status_code=201, response_model=DriverResponse)
async def create_driver(
    data: DriverCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> DriverResponse:
    """Add a new driver."""
    result = await service.create_driver(db, school.id, data.model_dump(), user.id)
    return DriverResponse(**result)


@router.put("/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: uuid.UUID,
    data: DriverUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> DriverResponse:
    """Update driver details."""
    result = await service.update_driver(
        db, school.id, driver_id, data.model_dump(exclude_unset=True), user.id
    )
    return DriverResponse(**result)


@router.delete("/drivers/{driver_id}", response_model=DriverDeleteResponse)
async def delete_driver(
    driver_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> DriverDeleteResponse:
    """Soft-delete a driver."""
    result = await service.delete_driver(db, school.id, driver_id, user.id)
    return DriverDeleteResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/helpers", response_model=HelperListResponse)
async def list_helpers(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> HelperListResponse:
    """List all helpers with optional filters."""
    result = await service.list_helpers(db, school.id, pagination, search, status)
    return HelperListResponse(**result)


@router.post("/helpers", status_code=201, response_model=HelperResponse)
async def create_helper(
    data: HelperCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> HelperResponse:
    """Add a new helper."""
    result = await service.create_helper(db, school.id, data.model_dump(), user.id)
    return HelperResponse(**result)


@router.put("/helpers/{helper_id}", response_model=HelperResponse)
async def update_helper(
    helper_id: uuid.UUID,
    data: HelperUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> HelperResponse:
    """Update helper details."""
    result = await service.update_helper(
        db, school.id, helper_id, data.model_dump(exclude_unset=True), user.id
    )
    return HelperResponse(**result)


@router.delete("/helpers/{helper_id}", response_model=HelperDeleteResponse)
async def delete_helper(
    helper_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> HelperDeleteResponse:
    """Soft-delete a helper."""
    result = await service.delete_helper(db, school.id, helper_id, user.id)
    return HelperDeleteResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/routes", response_model=RouteListResponse)
async def list_routes(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> RouteListResponse:
    """List all routes with optional filters."""
    result = await service.list_routes(db, school.id, pagination, search, status)
    return RouteListResponse(**result)


@router.post("/routes", status_code=201, response_model=RouteResponse)
async def create_route(
    data: RouteCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RouteResponse:
    """Create a new route."""
    result = await service.create_route(db, school.id, data.model_dump(), user.id)
    return RouteResponse(**result)


@router.put("/routes/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: uuid.UUID,
    data: RouteUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RouteResponse:
    """Update route details."""
    result = await service.update_route(
        db, school.id, route_id, data.model_dump(exclude_unset=True), user.id
    )
    return RouteResponse(**result)


@router.delete("/routes/{route_id}", response_model=RouteDeleteResponse)
async def delete_route(
    route_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> RouteDeleteResponse:
    """Soft-delete a route."""
    result = await service.delete_route(db, school.id, route_id, user.id)
    return RouteDeleteResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Assignments
# ────────────────────────────────────────────────────────────────────────────────


@router.get("/assignments", response_model=AssignmentListResponse)
async def list_assignments(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    status: str | None = Query(default=None),
    shift: str | None = Query(default=None),
) -> AssignmentListResponse:
    """List all route assignments (operational mappings)."""
    result = await service.list_assignments(db, school.id, pagination, status, shift)
    return AssignmentListResponse(**result)


@router.post("/assignments", status_code=201, response_model=AssignmentResponse)
async def create_assignment(
    data: AssignmentCreateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AssignmentResponse:
    """Create a route assignment. 409 if vehicle already assigned."""
    result = await service.create_assignment(db, school.id, data.model_dump(), user.id)
    return AssignmentResponse(**result)


@router.put("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: uuid.UUID,
    data: AssignmentUpdateRequest,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AssignmentResponse:
    """Update a route assignment."""
    result = await service.update_assignment(
        db, school.id, assignment_id, data.model_dump(exclude_unset=True), user.id
    )
    return AssignmentResponse(**result)


@router.delete("/assignments/{assignment_id}", response_model=AssignmentDeleteResponse)
async def delete_assignment(
    assignment_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
) -> AssignmentDeleteResponse:
    """Soft-delete an assignment. Frees vehicle, driver, and helper."""
    result = await service.delete_assignment(db, school.id, assignment_id, user.id)
    return AssignmentDeleteResponse(**result)


# ────────────────────────────────────────────────────────────────────────────────
# Route Students
# ────────────────────────────────────────────────────────────────────────────────


@router.post("/routes/shuffle-assign")
async def shuffle_assign_students(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Shuffle all day-scholar students and distribute across routes based on vehicle capacity."""
    return await service.shuffle_assign_students(db, school.id, user.id)


@router.get("/routes/{route_id}/students")
async def list_route_students(
    route_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """List students assigned to a route."""
    return await service.list_route_students(db, school.id, route_id)


@router.post("/routes/{route_id}/students")
async def assign_students_to_route(
    route_id: uuid.UUID,
    data: dict,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Assign students to a route. Body: { student_ids: [], pickup_point?, drop_point? }"""
    return await service.assign_students_to_route(db, school.id, route_id, data, user.id)


@router.delete("/routes/{route_id}/students/{student_id}")
async def remove_student_from_route(
    route_id: uuid.UUID,
    student_id: uuid.UUID,
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
):
    """Remove a student from a route."""
    return await service.remove_student_from_route(db, school.id, route_id, student_id)
