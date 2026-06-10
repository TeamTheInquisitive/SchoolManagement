from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, NotFound
from src.core.pagination import PaginationParams, paginate
from src.models.core import AcademicYear
from src.models.transport import (
    Driver,
    Helper,
    Route,
    RouteAssignment,
    StudentTransport,
    Vehicle,
)


# ────────────────────────────────────────────────────────────────────────────────
# Stats
# ────────────────────────────────────────────────────────────────────────────────


async def get_transport_stats(db: AsyncSession, school_id: uuid.UUID) -> dict:
    """Get transport KPI summary."""
    # Vehicles
    v_result = await db.execute(
        select(
            func.count(Vehicle.id).label("total"),
            func.sum(case((Vehicle.status == "Operational", 1), else_=0)).label("operational"),
            func.sum(case((Vehicle.status == "Maintenance", 1), else_=0)).label("maintenance"),
            func.sum(case((Vehicle.status == "Out-Of-Order", 1), else_=0)).label("out_of_order"),
        ).where(Vehicle.school_id == school_id, Vehicle.is_active.is_(True))
    )
    v_row = v_result.one()

    # Drivers
    d_result = await db.execute(
        select(
            func.count(Driver.id).label("total"),
            func.sum(case((Driver.status == "Active", 1), else_=0)).label("active"),
            func.sum(case((Driver.status == "Available", 1), else_=0)).label("available"),
        ).where(Driver.school_id == school_id, Driver.is_active.is_(True))
    )
    d_row = d_result.one()

    # Helpers
    h_result = await db.execute(
        select(func.count(Helper.id)).where(
            Helper.school_id == school_id, Helper.is_active.is_(True)
        )
    )
    total_helpers = h_result.scalar() or 0

    # Active routes
    r_result = await db.execute(
        select(func.count(Route.id)).where(
            Route.school_id == school_id,
            Route.is_active.is_(True),
            Route.status == "Active",
        )
    )
    active_routes = r_result.scalar() or 0

    # Total assignments
    a_result = await db.execute(
        select(func.count(RouteAssignment.id)).where(
            RouteAssignment.school_id == school_id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        )
    )
    total_assignments = a_result.scalar() or 0

    # Total students transported (current academic year)
    ay_result = await db.execute(
        select(AcademicYear.id).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay_id = ay_result.scalar_one_or_none()

    total_students = 0
    if ay_id:
        st_result = await db.execute(
            select(func.count(StudentTransport.id)).where(
                StudentTransport.school_id == school_id,
                StudentTransport.academic_year_id == ay_id,
                StudentTransport.is_active.is_(True),
            )
        )
        total_students = st_result.scalar() or 0

    return {
        "total_vehicles": v_row.total,
        "operational_vehicles": v_row.operational,
        "under_maintenance": v_row.maintenance,
        "out_of_order": v_row.out_of_order,
        "total_drivers": d_row.total,
        "active_drivers": d_row.active,
        "available_drivers": d_row.available,
        "total_helpers": total_helpers,
        "active_routes": active_routes,
        "total_assignments": total_assignments,
        "total_students_transported": total_students,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Vehicles
# ────────────────────────────────────────────────────────────────────────────────


async def _enrich_vehicle(db: AsyncSession, vehicle: Vehicle) -> dict:
    """Enrich vehicle with assignment info (driver + route)."""
    driver_id = None
    driver_name = None
    route_id = None
    route_name = None

    assignment_result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.school_id == vehicle.school_id,
            RouteAssignment.vehicle_id == vehicle.id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        ).limit(1)
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment:
        # Get driver name
        drv_result = await db.execute(select(Driver.full_name).where(Driver.id == assignment.driver_id))
        drv_name = drv_result.scalar_one_or_none()
        driver_id = assignment.driver_id
        driver_name = drv_name

        # Get route name
        rt_result = await db.execute(select(Route.name).where(Route.id == assignment.route_id))
        rt_name = rt_result.scalar_one_or_none()
        route_id = assignment.route_id
        route_name = rt_name

    return {
        "id": vehicle.id,
        "vehicle_number": vehicle.vehicle_number,
        "plate_number": vehicle.plate_number,
        "type": vehicle.type,
        "model": vehicle.model,
        "year": vehicle.year,
        "fuel_type": vehicle.fuel_type,
        "capacity": vehicle.capacity,
        "occupied_seats": vehicle.occupied_seats,
        "status": vehicle.status,
        "driver_id": driver_id,
        "driver_name": driver_name,
        "route_id": route_id,
        "route_name": route_name,
        "next_service_date": vehicle.next_service_date,
        "insurance_expiry": vehicle.insurance_expiry,
        "fitness_expiry": vehicle.fitness_expiry,
        "is_active": vehicle.is_active,
        "created_at": vehicle.created_at,
        "metadata": vehicle.metadata_,
    }


async def list_vehicles(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    vehicle_type: str | None = None,
    status: str | None = None,
) -> dict:
    """List vehicles with filters and pagination."""
    query = select(Vehicle).where(Vehicle.school_id == school_id, Vehicle.is_active.is_(True))

    if search:
        query = query.where(
            or_(
                Vehicle.vehicle_number.ilike(f"%{search}%"),
                Vehicle.plate_number.ilike(f"%{search}%"),
                Vehicle.model.ilike(f"%{search}%"),
            )
        )
    if vehicle_type:
        query = query.where(Vehicle.type == vehicle_type)
    if status:
        query = query.where(Vehicle.status == status)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Vehicle.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    vehicles = result.scalars().all()

    items = []
    for v in vehicles:
        items.append(await _enrich_vehicle(db, v))

    return paginate(items, total, pagination)


async def create_vehicle(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a new vehicle."""
    # Check uniqueness
    existing = await db.execute(
        select(Vehicle).where(
            Vehicle.school_id == school_id,
            Vehicle.vehicle_number == data["vehicle_number"],
            Vehicle.is_active.is_(True),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Vehicle with number {data['vehicle_number']} already exists")

    vehicle = Vehicle(
        school_id=school_id,
        created_by=created_by,
        **data,
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return await _enrich_vehicle(db, vehicle)


async def get_vehicle(db: AsyncSession, school_id: uuid.UUID, vehicle_id: uuid.UUID) -> dict:
    """Get vehicle details."""
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.school_id == school_id,
            Vehicle.is_active.is_(True),
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise NotFound("Vehicle", str(vehicle_id))
    return await _enrich_vehicle(db, vehicle)


async def update_vehicle(
    db: AsyncSession, school_id: uuid.UUID, vehicle_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update vehicle details."""
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.school_id == school_id,
            Vehicle.is_active.is_(True),
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise NotFound("Vehicle", str(vehicle_id))

    # Check uniqueness if vehicle_number is being updated
    if data.get("vehicle_number") and data["vehicle_number"] != vehicle.vehicle_number:
        existing = await db.execute(
            select(Vehicle).where(
                Vehicle.school_id == school_id,
                Vehicle.vehicle_number == data["vehicle_number"],
                Vehicle.is_active.is_(True),
                Vehicle.id != vehicle_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"Vehicle with number {data['vehicle_number']} already exists")

    for key, value in data.items():
        if value is not None:
            setattr(vehicle, key, value)
    vehicle.updated_by = updated_by

    await db.commit()
    await db.refresh(vehicle)
    return await _enrich_vehicle(db, vehicle)


async def delete_vehicle(
    db: AsyncSession, school_id: uuid.UUID, vehicle_id: uuid.UUID, deleted_by: uuid.UUID
) -> dict:
    """Soft-delete a vehicle."""
    result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.school_id == school_id,
            Vehicle.is_active.is_(True),
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise NotFound("Vehicle", str(vehicle_id))

    vehicle.is_active = False
    vehicle.deleted_at = datetime.now(timezone.utc)
    vehicle.deleted_by = deleted_by
    vehicle.status = "Out-Of-Order"

    await db.commit()
    return {
        "id": vehicle.id,
        "vehicle_number": vehicle.vehicle_number,
        "status": "Inactive",
        "deactivated_on": str(date.today()),
        "message": "Vehicle deactivated. Historical records preserved.",
    }


async def export_vehicles(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """Export all vehicles as a list of dicts for CSV."""
    result = await db.execute(
        select(Vehicle).where(Vehicle.school_id == school_id, Vehicle.is_active.is_(True))
        .order_by(Vehicle.vehicle_number)
    )
    vehicles = result.scalars().all()

    rows = []
    for v in vehicles:
        rows.append({
            "vehicle_number": v.vehicle_number,
            "plate_number": v.plate_number or "",
            "type": v.type,
            "model": v.model or "",
            "year": v.year or "",
            "fuel_type": v.fuel_type or "",
            "capacity": v.capacity,
            "occupied_seats": v.occupied_seats,
            "status": v.status,
            "next_service_date": str(v.next_service_date) if v.next_service_date else "",
            "insurance_expiry": str(v.insurance_expiry) if v.insurance_expiry else "",
            "fitness_expiry": str(v.fitness_expiry) if v.fitness_expiry else "",
        })
    return rows


# ────────────────────────────────────────────────────────────────────────────────
# Drivers
# ────────────────────────────────────────────────────────────────────────────────


async def _generate_driver_id(db: AsyncSession, school_id: uuid.UUID) -> str:
    """Generate next driver_id like DRV001, DRV002..."""
    result = await db.execute(
        select(func.count(Driver.id)).where(Driver.school_id == school_id)
    )
    count = (result.scalar() or 0) + 1
    return f"DRV{count:03d}"


async def _enrich_driver(db: AsyncSession, driver: Driver) -> dict:
    """Enrich driver with assignment info."""
    assigned_vehicle_id = None
    assigned_vehicle = None
    assigned_route = None

    assignment_result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.school_id == driver.school_id,
            RouteAssignment.driver_id == driver.id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        ).limit(1)
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment:
        veh_result = await db.execute(
            select(Vehicle.id, Vehicle.vehicle_number).where(Vehicle.id == assignment.vehicle_id)
        )
        veh_row = veh_result.one_or_none()
        if veh_row:
            assigned_vehicle_id = veh_row[0]
            assigned_vehicle = veh_row[1]

        rt_result = await db.execute(select(Route.name).where(Route.id == assignment.route_id))
        rt_name = rt_result.scalar_one_or_none()
        assigned_route = rt_name

    return {
        "id": driver.id,
        "driver_id": driver.driver_id,
        "full_name": driver.full_name,
        "phone": driver.phone,
        "email": driver.email,
        "license_number": driver.license_number,
        "license_type": driver.license_type,
        "license_expiry": driver.license_expiry,
        "experience_years": driver.experience_years,
        "join_date": driver.join_date,
        "status": driver.status,
        "assigned_vehicle_id": assigned_vehicle_id,
        "assigned_vehicle": assigned_vehicle,
        "assigned_route": assigned_route,
        "emergency_contact_name": driver.emergency_contact_name,
        "emergency_contact_phone": driver.emergency_contact_phone,
        "is_active": driver.is_active,
        "created_at": driver.created_at,
        "metadata": driver.metadata_,
    }


async def list_drivers(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    status: str | None = None,
    license_type: str | None = None,
) -> dict:
    """List drivers with filters and pagination."""
    query = select(Driver).where(Driver.school_id == school_id, Driver.is_active.is_(True))

    if search:
        query = query.where(
            or_(
                Driver.full_name.ilike(f"%{search}%"),
                Driver.phone.ilike(f"%{search}%"),
                Driver.driver_id.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Driver.status == status)
    if license_type:
        query = query.where(Driver.license_type == license_type)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Driver.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    drivers = result.scalars().all()

    items = []
    for d in drivers:
        items.append(await _enrich_driver(db, d))

    return paginate(items, total, pagination)


async def create_driver(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a new driver."""
    driver_id = await _generate_driver_id(db, school_id)

    driver = Driver(
        school_id=school_id,
        driver_id=driver_id,
        created_by=created_by,
        status="Available",
        **data,
    )
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    return await _enrich_driver(db, driver)


async def update_driver(
    db: AsyncSession, school_id: uuid.UUID, driver_uuid: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update driver details."""
    result = await db.execute(
        select(Driver).where(
            Driver.id == driver_uuid,
            Driver.school_id == school_id,
            Driver.is_active.is_(True),
        )
    )
    driver = result.scalar_one_or_none()
    if not driver:
        raise NotFound("Driver", str(driver_uuid))

    for key, value in data.items():
        if value is not None:
            setattr(driver, key, value)
    driver.updated_by = updated_by

    await db.commit()
    await db.refresh(driver)
    return await _enrich_driver(db, driver)


async def delete_driver(
    db: AsyncSession, school_id: uuid.UUID, driver_uuid: uuid.UUID, deleted_by: uuid.UUID
) -> dict:
    """Soft-delete a driver."""
    result = await db.execute(
        select(Driver).where(
            Driver.id == driver_uuid,
            Driver.school_id == school_id,
            Driver.is_active.is_(True),
        )
    )
    driver = result.scalar_one_or_none()
    if not driver:
        raise NotFound("Driver", str(driver_uuid))

    driver.is_active = False
    driver.deleted_at = datetime.now(timezone.utc)
    driver.deleted_by = deleted_by
    driver.status = "Inactive"

    await db.commit()
    return {
        "id": driver.id,
        "driver_id": driver.driver_id,
        "full_name": driver.full_name,
        "status": "Inactive",
        "deactivated_on": str(date.today()),
        "message": "Driver deactivated. Historical records preserved.",
    }


async def export_drivers(db: AsyncSession, school_id: uuid.UUID) -> list[dict]:
    """Export all drivers as a list of dicts for CSV."""
    result = await db.execute(
        select(Driver).where(Driver.school_id == school_id, Driver.is_active.is_(True))
        .order_by(Driver.driver_id)
    )
    drivers = result.scalars().all()

    rows = []
    for d in drivers:
        rows.append({
            "driver_id": d.driver_id,
            "full_name": d.full_name,
            "phone": d.phone,
            "email": d.email or "",
            "license_number": d.license_number,
            "license_type": d.license_type or "",
            "license_expiry": str(d.license_expiry) if d.license_expiry else "",
            "experience_years": d.experience_years or "",
            "join_date": str(d.join_date) if d.join_date else "",
            "status": d.status,
            "emergency_contact_name": d.emergency_contact_name or "",
            "emergency_contact_phone": d.emergency_contact_phone or "",
        })
    return rows


# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────


async def _generate_helper_id(db: AsyncSession, school_id: uuid.UUID) -> str:
    """Generate next helper_id like HLP001, HLP002..."""
    result = await db.execute(
        select(func.count(Helper.id)).where(Helper.school_id == school_id)
    )
    count = (result.scalar() or 0) + 1
    return f"HLP{count:03d}"


async def _enrich_helper(db: AsyncSession, helper: Helper) -> dict:
    """Enrich helper with assignment info."""
    assigned_vehicle_id = None
    assigned_vehicle = None
    assigned_route = None

    assignment_result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.school_id == helper.school_id,
            RouteAssignment.helper_id == helper.id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        ).limit(1)
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment:
        veh_result = await db.execute(
            select(Vehicle.id, Vehicle.vehicle_number).where(Vehicle.id == assignment.vehicle_id)
        )
        veh_row = veh_result.one_or_none()
        if veh_row:
            assigned_vehicle_id = veh_row[0]
            assigned_vehicle = veh_row[1]

        rt_result = await db.execute(select(Route.name).where(Route.id == assignment.route_id))
        rt_name = rt_result.scalar_one_or_none()
        assigned_route = rt_name

    return {
        "id": helper.id,
        "helper_id": helper.helper_id,
        "full_name": helper.full_name,
        "phone": helper.phone,
        "join_date": helper.join_date,
        "status": helper.status,
        "assigned_vehicle_id": assigned_vehicle_id,
        "assigned_vehicle": assigned_vehicle,
        "assigned_route": assigned_route,
        "is_active": helper.is_active,
        "created_at": helper.created_at,
        "metadata": helper.metadata_,
    }


async def list_helpers(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    status: str | None = None,
) -> dict:
    """List helpers with filters and pagination."""
    query = select(Helper).where(Helper.school_id == school_id, Helper.is_active.is_(True))

    if search:
        query = query.where(
            or_(
                Helper.full_name.ilike(f"%{search}%"),
                Helper.phone.ilike(f"%{search}%"),
                Helper.helper_id.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Helper.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Helper.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    helpers = result.scalars().all()

    items = []
    for h in helpers:
        items.append(await _enrich_helper(db, h))

    return paginate(items, total, pagination)


async def create_helper(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a new helper."""
    helper_id = await _generate_helper_id(db, school_id)

    helper = Helper(
        school_id=school_id,
        helper_id=helper_id,
        created_by=created_by,
        status="Available",
        **data,
    )
    db.add(helper)
    await db.commit()
    await db.refresh(helper)
    return await _enrich_helper(db, helper)


async def update_helper(
    db: AsyncSession, school_id: uuid.UUID, helper_uuid: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update helper details."""
    result = await db.execute(
        select(Helper).where(
            Helper.id == helper_uuid,
            Helper.school_id == school_id,
            Helper.is_active.is_(True),
        )
    )
    helper = result.scalar_one_or_none()
    if not helper:
        raise NotFound("Helper", str(helper_uuid))

    for key, value in data.items():
        if value is not None:
            setattr(helper, key, value)
    helper.updated_by = updated_by

    await db.commit()
    await db.refresh(helper)
    return await _enrich_helper(db, helper)


async def delete_helper(
    db: AsyncSession, school_id: uuid.UUID, helper_uuid: uuid.UUID, deleted_by: uuid.UUID
) -> dict:
    """Soft-delete a helper."""
    result = await db.execute(
        select(Helper).where(
            Helper.id == helper_uuid,
            Helper.school_id == school_id,
            Helper.is_active.is_(True),
        )
    )
    helper = result.scalar_one_or_none()
    if not helper:
        raise NotFound("Helper", str(helper_uuid))

    helper.is_active = False
    helper.deleted_at = datetime.now(timezone.utc)
    helper.deleted_by = deleted_by
    helper.status = "Inactive"

    await db.commit()
    return {
        "id": helper.id,
        "helper_id": helper.helper_id,
        "full_name": helper.full_name,
        "status": "Inactive",
        "deactivated_on": str(date.today()),
        "message": "Helper deactivated. Historical records preserved.",
    }


# ────────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────────


async def _generate_route_code(db: AsyncSession, school_id: uuid.UUID) -> str:
    """Generate next route_code like R-001, R-002..."""
    result = await db.execute(
        select(func.count(Route.id)).where(Route.school_id == school_id)
    )
    count = (result.scalar() or 0) + 1
    return f"R-{count:03d}"


async def _enrich_route(db: AsyncSession, route: Route) -> dict:
    """Enrich route with assignment info and student count."""
    assigned_vehicle = None
    assigned_driver = None

    vehicle_capacity = 0

    assignment_result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.school_id == route.school_id,
            RouteAssignment.route_id == route.id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        ).limit(1)
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment:
        veh_result = await db.execute(
            select(Vehicle).where(Vehicle.id == assignment.vehicle_id)
        )
        vehicle = veh_result.scalar_one_or_none()
        if vehicle:
            assigned_vehicle = vehicle.vehicle_number
            vehicle_capacity = vehicle.capacity or 0

        drv_result = await db.execute(
            select(Driver.full_name).where(Driver.id == assignment.driver_id)
        )
        assigned_driver = drv_result.scalar_one_or_none()

    # Student count for this route
    st_result = await db.execute(
        select(func.count(StudentTransport.id)).where(
            StudentTransport.school_id == route.school_id,
            StudentTransport.route_id == route.id,
            StudentTransport.is_active.is_(True),
        )
    )
    students_count = st_result.scalar() or 0

    # Stops: the spec shows stops as a number in list, but stored as JSONB
    stops_value = route.stops
    if isinstance(stops_value, list):
        stops_display = len(stops_value)
    elif isinstance(stops_value, int):
        stops_display = stops_value
    else:
        stops_display = stops_value

    return {
        "id": route.id,
        "route_code": route.route_code,
        "name": route.name,
        "area": route.area,
        "shift": route.shift,
        "stops": stops_display,
        "distance_km": route.distance_km,
        "start_time": route.start_time,
        "end_time": route.end_time,
        "status": route.status,
        "assigned_vehicle": assigned_vehicle,
        "assigned_driver": assigned_driver,
        "capacity": vehicle_capacity,
        "students_count": students_count,
        "is_active": route.is_active,
        "created_at": route.created_at,
        "metadata": route.metadata_,
    }


async def list_routes(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    status: str | None = None,
) -> dict:
    """List routes with filters and pagination."""
    query = select(Route).where(Route.school_id == school_id, Route.is_active.is_(True))

    if search:
        query = query.where(
            or_(
                Route.name.ilike(f"%{search}%"),
                Route.route_code.ilike(f"%{search}%"),
                Route.area.ilike(f"%{search}%"),
            )
        )
    if status:
        query = query.where(Route.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Route.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    routes = result.scalars().all()

    items = []
    for r in routes:
        items.append(await _enrich_route(db, r))

    return paginate(items, total, pagination)


async def create_route(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a new route."""
    route_code = await _generate_route_code(db, school_id)

    # Handle stops: accept int or list
    stops_val = data.pop("stops", None)
    if isinstance(stops_val, int):
        stops_db = []  # store as empty list, integer is just count for display
    elif isinstance(stops_val, list):
        stops_db = stops_val
    else:
        stops_db = []

    route = Route(
        school_id=school_id,
        route_code=route_code,
        created_by=created_by,
        stops=stops_db,
        **data,
    )
    db.add(route)
    await db.commit()
    await db.refresh(route)
    return await _enrich_route(db, route)


async def update_route(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID, data: dict, updated_by: uuid.UUID
) -> dict:
    """Update route details."""
    result = await db.execute(
        select(Route).where(
            Route.id == route_id,
            Route.school_id == school_id,
            Route.is_active.is_(True),
        )
    )
    route = result.scalar_one_or_none()
    if not route:
        raise NotFound("Route", str(route_id))

    # Handle stops separately
    if "stops" in data:
        stops_val = data.pop("stops")
        if isinstance(stops_val, int):
            pass  # don't update the JSONB with an int
        elif isinstance(stops_val, list):
            route.stops = stops_val
        elif stops_val is not None:
            route.stops = stops_val

    for key, value in data.items():
        if value is not None:
            setattr(route, key, value)
    route.updated_by = updated_by

    await db.commit()
    await db.refresh(route)
    return await _enrich_route(db, route)


async def delete_route(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID, deleted_by: uuid.UUID
) -> dict:
    """Soft-delete a route."""
    result = await db.execute(
        select(Route).where(
            Route.id == route_id,
            Route.school_id == school_id,
            Route.is_active.is_(True),
        )
    )
    route = result.scalar_one_or_none()
    if not route:
        raise NotFound("Route", str(route_id))

    route.is_active = False
    route.deleted_at = datetime.now(timezone.utc)
    route.deleted_by = deleted_by
    route.status = "Inactive"

    await db.commit()
    return {
        "id": route.id,
        "name": route.name,
        "status": "Inactive",
        "deactivated_on": str(date.today()),
        "message": "Route deactivated. Historical records preserved.",
    }


# ────────────────────────────────────────────────────────────────────────────────
# Route Assignments
# ────────────────────────────────────────────────────────────────────────────────


async def _enrich_assignment(db: AsyncSession, assignment: RouteAssignment) -> dict:
    """Build full assignment response with related entities."""
    # Route info
    rt_result = await db.execute(select(Route).where(Route.id == assignment.route_id))
    route = rt_result.scalar_one_or_none()

    # Vehicle info
    veh_result = await db.execute(select(Vehicle).where(Vehicle.id == assignment.vehicle_id))
    vehicle = veh_result.scalar_one_or_none()

    # Driver info
    drv_result = await db.execute(select(Driver).where(Driver.id == assignment.driver_id))
    driver = drv_result.scalar_one_or_none()

    # Helper info
    helper_name = None
    helper_phone = None
    if assignment.helper_id:
        hlp_result = await db.execute(select(Helper).where(Helper.id == assignment.helper_id))
        helper = hlp_result.scalar_one_or_none()
        if helper:
            helper_name = helper.full_name
            helper_phone = helper.phone

    stops_value = route.stops if route else None
    if isinstance(stops_value, list):
        stops_display = len(stops_value)
    elif isinstance(stops_value, int):
        stops_display = stops_value
    else:
        stops_display = stops_value

    return {
        "id": assignment.id,
        "route_id": assignment.route_id,
        "route_name": route.name if route else None,
        "route_code": route.route_code if route else None,
        "area": route.area if route else None,
        "shift": route.shift if route else None,
        "stops": stops_display,
        "distance_km": route.distance_km if route else None,
        "start_time": route.start_time if route else None,
        "end_time": route.end_time if route else None,
        "vehicle_id": assignment.vehicle_id,
        "vehicle_number": vehicle.vehicle_number if vehicle else None,
        "vehicle_type": vehicle.type if vehicle else None,
        "vehicle_capacity": vehicle.capacity if vehicle else None,
        "occupied_seats": vehicle.occupied_seats if vehicle else None,
        "driver_id": assignment.driver_id,
        "driver_name": driver.full_name if driver else None,
        "driver_phone": driver.phone if driver else None,
        "helper_id": assignment.helper_id,
        "helper_name": helper_name,
        "helper_phone": helper_phone,
        "status": assignment.status,
        "is_active": assignment.is_active,
        "created_at": assignment.created_at,
        "metadata": assignment.metadata_,
    }


async def list_assignments(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    status: str | None = None,
    shift: str | None = None,
) -> dict:
    """List route assignments with filters and pagination."""
    query = select(RouteAssignment).where(
        RouteAssignment.school_id == school_id,
        RouteAssignment.is_active.is_(True),
    )

    if status:
        query = query.where(RouteAssignment.status == status)

    # Filter by shift requires joining route
    if shift:
        query = query.join(Route, RouteAssignment.route_id == Route.id).where(
            Route.shift == shift
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(RouteAssignment.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    assignments = result.scalars().all()

    items = []
    for a in assignments:
        items.append(await _enrich_assignment(db, a))

    return paginate(items, total, pagination)


async def create_assignment(
    db: AsyncSession, school_id: uuid.UUID, data: dict, created_by: uuid.UUID
) -> dict:
    """Create a route assignment. Validates vehicle is not already assigned."""
    vehicle_id = data["vehicle_id"]
    driver_id = data["driver_id"]
    helper_id = data.get("helper_id")
    route_id = data["route_id"]

    # Check vehicle exists
    veh_result = await db.execute(
        select(Vehicle).where(
            Vehicle.id == vehicle_id,
            Vehicle.school_id == school_id,
            Vehicle.is_active.is_(True),
        )
    )
    vehicle = veh_result.scalar_one_or_none()
    if not vehicle:
        raise NotFound("Vehicle", str(vehicle_id))

    # Check vehicle not already assigned
    existing = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.school_id == school_id,
            RouteAssignment.vehicle_id == vehicle_id,
            RouteAssignment.is_active.is_(True),
            RouteAssignment.status == "Active",
        )
    )
    existing_assignment = existing.scalar_one_or_none()
    if existing_assignment:
        # Get route name for error message
        rt_result = await db.execute(
            select(Route.name).where(Route.id == existing_assignment.route_id)
        )
        rt_name = rt_result.scalar_one_or_none() or "Unknown"
        raise ConflictError(
            f"Vehicle {vehicle.vehicle_number} is already assigned to route {rt_name}"
        )

    # Check route exists
    rt_result = await db.execute(
        select(Route).where(
            Route.id == route_id,
            Route.school_id == school_id,
            Route.is_active.is_(True),
        )
    )
    if not rt_result.scalar_one_or_none():
        raise NotFound("Route", str(route_id))

    # Check driver exists
    drv_result = await db.execute(
        select(Driver).where(
            Driver.id == driver_id,
            Driver.school_id == school_id,
            Driver.is_active.is_(True),
        )
    )
    driver = drv_result.scalar_one_or_none()
    if not driver:
        raise NotFound("Driver", str(driver_id))

    # Check helper exists (if provided)
    helper = None
    if helper_id:
        hlp_result = await db.execute(
            select(Helper).where(
                Helper.id == helper_id,
                Helper.school_id == school_id,
                Helper.is_active.is_(True),
            )
        )
        helper = hlp_result.scalar_one_or_none()
        if not helper:
            raise NotFound("Helper", str(helper_id))

    # Create assignment
    assignment = RouteAssignment(
        school_id=school_id,
        route_id=route_id,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        helper_id=helper_id,
        status="Active",
        created_by=created_by,
    )
    db.add(assignment)

    # Update driver status to Active
    driver.status = "Active"

    # Update helper status to Active
    if helper:
        helper.status = "Active"

    await db.commit()
    await db.refresh(assignment)
    return await _enrich_assignment(db, assignment)


async def update_assignment(
    db: AsyncSession,
    school_id: uuid.UUID,
    assignment_id: uuid.UUID,
    data: dict,
    updated_by: uuid.UUID,
) -> dict:
    """Update a route assignment."""
    result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.id == assignment_id,
            RouteAssignment.school_id == school_id,
            RouteAssignment.is_active.is_(True),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Route Assignment", str(assignment_id))

    # If vehicle is changing, check new vehicle isn't already assigned
    new_vehicle_id = data.get("vehicle_id")
    if new_vehicle_id and new_vehicle_id != assignment.vehicle_id:
        existing = await db.execute(
            select(RouteAssignment).where(
                RouteAssignment.school_id == school_id,
                RouteAssignment.vehicle_id == new_vehicle_id,
                RouteAssignment.is_active.is_(True),
                RouteAssignment.status == "Active",
                RouteAssignment.id != assignment_id,
            )
        )
        if existing.scalar_one_or_none():
            veh_result = await db.execute(
                select(Vehicle.vehicle_number).where(Vehicle.id == new_vehicle_id)
            )
            veh_number = veh_result.scalar_one_or_none() or "Unknown"
            raise ConflictError(f"Vehicle {veh_number} is already assigned to another route")

    # Track old driver/helper for status update
    old_driver_id = assignment.driver_id
    old_helper_id = assignment.helper_id

    # Apply updates
    for key, value in data.items():
        if value is not None:
            setattr(assignment, key, value)
    assignment.updated_by = updated_by

    # Update driver statuses
    new_driver_id = data.get("driver_id")
    if new_driver_id and new_driver_id != old_driver_id:
        # Set old driver to Available
        old_drv = await db.execute(select(Driver).where(Driver.id == old_driver_id))
        old_driver = old_drv.scalar_one_or_none()
        if old_driver:
            old_driver.status = "Available"
        # Set new driver to Active
        new_drv = await db.execute(select(Driver).where(Driver.id == new_driver_id))
        new_driver = new_drv.scalar_one_or_none()
        if new_driver:
            new_driver.status = "Active"

    # Update helper statuses
    new_helper_id = data.get("helper_id")
    if new_helper_id != old_helper_id:
        if old_helper_id:
            old_hlp = await db.execute(select(Helper).where(Helper.id == old_helper_id))
            old_helper = old_hlp.scalar_one_or_none()
            if old_helper:
                old_helper.status = "Available"
        if new_helper_id:
            new_hlp = await db.execute(select(Helper).where(Helper.id == new_helper_id))
            new_helper = new_hlp.scalar_one_or_none()
            if new_helper:
                new_helper.status = "Active"

    await db.commit()
    await db.refresh(assignment)
    return await _enrich_assignment(db, assignment)


async def delete_assignment(
    db: AsyncSession, school_id: uuid.UUID, assignment_id: uuid.UUID, deleted_by: uuid.UUID
) -> dict:
    """Soft-delete an assignment. Frees vehicle, driver, helper."""
    result = await db.execute(
        select(RouteAssignment).where(
            RouteAssignment.id == assignment_id,
            RouteAssignment.school_id == school_id,
            RouteAssignment.is_active.is_(True),
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise NotFound("Route Assignment", str(assignment_id))

    # Get route name for response
    rt_result = await db.execute(select(Route.name).where(Route.id == assignment.route_id))
    route_name = rt_result.scalar_one_or_none() or "Unknown"

    # Set driver back to Available
    drv_result = await db.execute(select(Driver).where(Driver.id == assignment.driver_id))
    driver = drv_result.scalar_one_or_none()
    if driver:
        driver.status = "Available"

    # Set helper back to Available
    if assignment.helper_id:
        hlp_result = await db.execute(select(Helper).where(Helper.id == assignment.helper_id))
        helper = hlp_result.scalar_one_or_none()
        if helper:
            helper.status = "Available"

    # Deactivate assignment
    assignment.is_active = False
    assignment.deleted_at = datetime.now(timezone.utc)
    assignment.deleted_by = deleted_by
    assignment.status = "Inactive"

    await db.commit()
    return {
        "id": assignment.id,
        "route_name": route_name,
        "status": "Inactive",
        "deactivated_on": str(date.today()),
        "message": "Assignment removed. Vehicle, driver, and helper are now available.",
    }


# ────────────────────────────────────────────────────────────────────────────────
# Route Students
# ────────────────────────────────────────────────────────────────────────────────


async def list_route_students(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID
) -> dict:
    """List students assigned to a route for current academic year."""
    from src.models.student import Student, StudentEnrollment
    from src.models.academic import ClassSection, Class, Section

    ay_result = await db.execute(
        select(AcademicYear.id).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay_id = ay_result.scalar_one_or_none()
    if not ay_id:
        return {"students": [], "count": 0}

    result = await db.execute(
        select(StudentTransport, Student.full_name, Student.admission_number)
        .join(Student, Student.id == StudentTransport.student_id)
        .where(
            StudentTransport.school_id == school_id,
            StudentTransport.route_id == route_id,
            StudentTransport.academic_year_id == ay_id,
            StudentTransport.is_active.is_(True),
        )
        .order_by(Student.full_name)
    )
    rows = result.all()

    # Get class/section for each student
    student_ids = [st.student_id for st, _, _ in rows]
    class_map = {}
    if student_ids:
        enr_result = await db.execute(
            select(StudentEnrollment.student_id, Class.name, Section.name)
            .join(ClassSection, ClassSection.id == StudentEnrollment.class_section_id)
            .join(Class, Class.id == ClassSection.class_id)
            .join(Section, Section.id == ClassSection.section_id)
            .where(
                StudentEnrollment.student_id.in_(student_ids),
                StudentEnrollment.academic_year_id == ay_id,
                StudentEnrollment.is_active.is_(True),
            )
        )
        for sid, cls_name, sec_name in enr_result.all():
            class_map[sid] = {"class_name": cls_name, "section": sec_name}

    return {
        "students": [
            {
                "id": str(st.id),
                "student_id": str(st.student_id),
                "student_name": name,
                "admission_number": adm,
                "class_name": class_map.get(st.student_id, {}).get("class_name", ""),
                "section": class_map.get(st.student_id, {}).get("section", ""),
                "pickup_point": st.pickup_point,
                "drop_point": st.drop_point,
            }
            for st, name, adm in rows
        ],
        "count": len(rows),
    }


async def assign_students_to_route(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID, data: dict, user_id: uuid.UUID
) -> dict:
    """Assign students to a route."""
    ay_result = await db.execute(
        select(AcademicYear.id).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay_id = ay_result.scalar_one_or_none()
    if not ay_id:
        raise AppException(status_code=400, error="No active academic year")

    student_ids = data.get("student_ids", [])
    pickup = data.get("pickup_point")
    drop = data.get("drop_point")
    count = 0

    for sid in student_ids:
        # Check if already assigned
        existing = await db.execute(
            select(StudentTransport).where(
                StudentTransport.school_id == school_id,
                StudentTransport.student_id == uuid.UUID(sid),
                StudentTransport.academic_year_id == ay_id,
                StudentTransport.is_active.is_(True),
            )
        )
        ex = existing.scalar_one_or_none()
        if ex:
            # Update route
            ex.route_id = route_id
            ex.pickup_point = pickup
            ex.drop_point = drop
        else:
            db.add(StudentTransport(
                school_id=school_id,
                student_id=uuid.UUID(sid),
                route_id=route_id,
                academic_year_id=ay_id,
                pickup_point=pickup,
                drop_point=drop,
                created_by=user_id,
            ))
        count += 1

    # Update vehicle occupied_seats
    await _update_route_capacity(db, school_id, route_id, ay_id)
    await db.commit()
    return {"assigned": count, "message": f"{count} student(s) assigned to route"}


async def remove_student_from_route(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID, student_id: uuid.UUID
) -> dict:
    """Remove a student from a route."""
    ay_result = await db.execute(
        select(AcademicYear.id).where(
            AcademicYear.school_id == school_id,
            AcademicYear.is_current.is_(True),
            AcademicYear.is_active.is_(True),
        )
    )
    ay_id = ay_result.scalar_one_or_none()

    result = await db.execute(
        select(StudentTransport).where(
            StudentTransport.school_id == school_id,
            StudentTransport.route_id == route_id,
            StudentTransport.student_id == student_id,
            StudentTransport.is_active.is_(True),
        )
    )
    record = result.scalar_one_or_none()
    if record:
        record.is_active = False

    if ay_id:
        await _update_route_capacity(db, school_id, route_id, ay_id)
    await db.commit()
    return {"message": "Student removed from route"}


async def _update_route_capacity(
    db: AsyncSession, school_id: uuid.UUID, route_id: uuid.UUID, ay_id: uuid.UUID
):
    """Update occupied_seats on the vehicle assigned to this route."""
    # Count active students on this route
    count_result = await db.execute(
        select(func.count(StudentTransport.id)).where(
            StudentTransport.school_id == school_id,
            StudentTransport.route_id == route_id,
            StudentTransport.academic_year_id == ay_id,
            StudentTransport.is_active.is_(True),
        )
    )
    student_count = count_result.scalar() or 0

    # Find vehicle assigned to this route
    assignment = await db.execute(
        select(RouteAssignment.vehicle_id).where(
            RouteAssignment.school_id == school_id,
            RouteAssignment.route_id == route_id,
            RouteAssignment.is_active.is_(True),
        )
    )
    vehicle_id = assignment.scalar_one_or_none()
    if vehicle_id:
        vehicle = await db.execute(
            select(Vehicle).where(Vehicle.id == vehicle_id)
        )
        v = vehicle.scalar_one_or_none()
        if v:
            v.occupied_seats = student_count


async def shuffle_assign_students(
    db: AsyncSession, school_id: uuid.UUID, user_id: uuid.UUID
) -> dict:
    """Shuffle day-scholar students and assign to routes based on vehicle capacity."""
    import random
    from src.models.student import Student, StudentEnrollment

    ay_result = await db.execute(
        select(AcademicYear.id).where(
            AcademicYear.school_id == school_id, AcademicYear.is_current.is_(True), AcademicYear.is_active.is_(True),
        )
    )
    ay_id = ay_result.scalar_one_or_none()
    if not ay_id:
        return {"message": "No active academic year", "assigned": 0}

    # Get all routes with their vehicle capacity (only Operational vehicles)
    routes_result = await db.execute(
        select(Route.id, RouteAssignment.vehicle_id)
        .outerjoin(RouteAssignment, and_(RouteAssignment.route_id == Route.id, RouteAssignment.is_active.is_(True)))
        .where(Route.school_id == school_id, Route.status == "Active", Route.is_active.is_(True))
    )
    route_capacities = []
    for route_id, vehicle_id in routes_result.all():
        capacity = 0
        if vehicle_id:
            v_r = await db.execute(select(Vehicle.capacity, Vehicle.status).where(Vehicle.id == vehicle_id))
            row = v_r.one_or_none()
            if row and row.status == "Operational":
                capacity = row.capacity or 0
        if capacity > 0:
            route_capacities.append({"route_id": route_id, "capacity": capacity})

    if not route_capacities:
        return {"message": "No routes with operational vehicles found", "assigned": 0}

    # Get all active day-scholar students (exclude hostellers)
    students_result = await db.execute(
        select(StudentEnrollment.student_id, Student.metadata_)
        .join(Student, Student.id == StudentEnrollment.student_id)
        .where(
            StudentEnrollment.school_id == school_id,
            StudentEnrollment.academic_year_id == ay_id,
            StudentEnrollment.status == "Active",
            StudentEnrollment.is_active.is_(True),
            Student.is_active.is_(True),
            Student.status == "Active",
        )
    )
    all_students = [(sid, meta) for sid, meta in students_result.all()]
    # Filter: only Day Scholar (exclude Hosteller)
    day_scholars = [sid for sid, meta in all_students if (meta or {}).get("student_type") != "Hosteller"]

    if not day_scholars:
        return {"message": "No day-scholar students found", "assigned": 0}

    # Remove existing transport assignments
    from sqlalchemy import delete as sa_delete
    await db.execute(
        sa_delete(StudentTransport).where(
            StudentTransport.school_id == school_id,
            StudentTransport.academic_year_id == ay_id,
        )
    )

    # Shuffle and distribute based on capacity
    random.shuffle(day_scholars)
    count = 0
    student_idx = 0
    for route_info in route_capacities:
        slots = route_info["capacity"]
        for _ in range(slots):
            if student_idx >= len(day_scholars):
                break
            db.add(StudentTransport(
                school_id=school_id,
                student_id=day_scholars[student_idx],
                route_id=route_info["route_id"],
                academic_year_id=ay_id,
                created_by=user_id,
            ))
            student_idx += 1
            count += 1
        # Update vehicle occupied_seats
        await _update_route_capacity(db, school_id, route_info["route_id"], ay_id)

    await db.commit()
    unassigned = len(day_scholars) - count
    return {"message": f"Assigned {count} students across {len(route_capacities)} routes" + (f" ({unassigned} unassigned - capacity full)" if unassigned > 0 else ""), "assigned": count}
