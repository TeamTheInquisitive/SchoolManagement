# List API Guidelines

**Last Updated:** 2026-06-13

Standard patterns for building any list/paginated API endpoint in this project. All new list APIs MUST follow these guidelines. Existing APIs should be migrated when touched.

---

## Execution Order (MANDATORY)

```
Dataset (base query with school_id + is_active)
  → JOINs (for filtering on related entities)
  → WHERE filters (status, type, category, etc.)
  → Search (ILIKE on relevant text fields)
  → Date range filters (if applicable)
  → COUNT (total matching records)
  → ORDER BY (sorting)
  → OFFSET/LIMIT (pagination)
  → Execute & build response
```

**NEVER:**
```
Dataset → Paginate → Filter (post-pagination filtering)
```

---

## Backend Implementation Pattern

### Router

```python
@router.get("", response_model=SomeListResponse)
async def list_items(
    db: SessionDep,
    school: SchoolDep,
    user: AdminUser,
    pagination: PaginationDep,
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    # Add all filter params as Query defaults
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
) -> SomeListResponse:
    """List items with filters and pagination."""
    result = await service.list_items(
        db, school.id, pagination, search, status, date_from, date_to
    )
    return SomeListResponse(**result)
```

### Service

```python
async def list_items(
    db: AsyncSession,
    school_id: uuid.UUID,
    pagination: PaginationParams,
    search: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    # 1. Base query
    query = select(Model).where(
        Model.school_id == school_id,
        Model.is_active.is_(True),
    )

    # 2. JOINs for related entity filtering (BEFORE pagination)
    if class_name or section:
        query = (
            query
            .join(RelatedModel, RelatedModel.item_id == Model.id)
            .join(Class, Class.id == RelatedModel.class_id)
        )
        if class_name:
            query = query.where(Class.name == class_name)

    # 3. Direct filters
    if status:
        query = query.where(Model.status == status)

    # 4. Search (case-insensitive, multiple fields)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Model.name.ilike(pattern),
                Model.email.ilike(pattern),
                Model.identifier.ilike(pattern),
            )
        )

    # 5. Date range
    if date_from:
        try:
            d = date.fromisoformat(date_from)
            query = query.where(Model.created_at >= d)
        except ValueError:
            pass
    if date_to:
        try:
            d = date.fromisoformat(date_to)
            query = query.where(Model.created_at <= d)
        except ValueError:
            pass

    # 6. COUNT after all filters
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 7. Sort then paginate
    query = query.order_by(Model.name).offset(pagination.offset).limit(pagination.page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # 8. Build response
    results = [_build_response(item) for item in items]
    return paginate(results, total, pagination)
```

---

## Response Format

```json
{
  "results": [...],
  "count": 47,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

- `count` = total filtered/searched records (NOT total rows in DB)
- `results` = items for current page only
- Empty results: `{ "results": [], "count": 0, "page": 1, "page_size": 20, "total_pages": 0 }`

---

## Rules

### Filtering

1. All filters apply to the FULL dataset before pagination
2. Use JOINs for filtering on related entities — never filter post-pagination with `continue`
3. Search must be case-insensitive (`ilike`)
4. Search should cover multiple relevant fields (name, email, ID)
5. Date filters should use `try/except` for parsing — never crash on bad input

### Pagination

1. Always respect `page_size` — return exactly `page_size` items (or fewer on last page)
2. `total` must represent filtered count, not unfiltered table count
3. Use `pagination.offset` and `pagination.page_size` from the shared helper
4. Page is 1-indexed from the frontend

### Performance

1. COUNT query should use `.select_from(query.subquery())` — not a separate query
2. Batch-fetch related data AFTER pagination (user info, parent info, etc.)
3. Use `selectinload()` for eager loading relationships when needed
4. Never do N+1 queries inside the pagination loop — batch with `.in_()`

---

## Anti-Patterns (DO NOT)

```python
# ❌ WRONG: Filtering after pagination
result = await db.execute(query.offset(...).limit(...))
items = result.scalars().all()
for item in items:
    if item.class_name != filter_class:
        continue  # SKIPS ITEMS, BREAKS PAGE SIZE

# ❌ WRONG: Count before filters
total = await db.execute(select(func.count(Model.id)))  # Counts ALL, not filtered
query = query.where(Model.status == status)  # Filter applied after count

# ❌ WRONG: Client-side search on paginated data
# Frontend:
const filtered = results.filter(r => r.name.includes(search))  # WRONG

# ❌ WRONG: N+1 inside loop
for item in items:
    enrollment = await db.execute(select(...).where(id == item.id))  # N queries!
```

---

## Frontend Requirements (for reference)

When consuming these APIs:

1. **Debounce search** — 300ms using `useDebounceValue` from `usehooks-ts`
2. **No client-side re-filtering** — trust the backend, render API results directly
3. **Reset page on filter change** — every filter `onChange` calls `pagination.reset()`
4. **All filters in query key** — ensures cache invalidation works correctly
5. **Use `placeholderData: (prev) => prev`** — keeps old data visible while loading new page

---

## Checklist for New List APIs

- [ ] Base query filters by `school_id` and `is_active`
- [ ] All user-facing filters are in WHERE clause before pagination
- [ ] Related entity filters use JOINs (not post-pagination loops)
- [ ] Search is case-insensitive across multiple fields
- [ ] Date range parsing is safe (try/except)
- [ ] COUNT is computed after ALL filters
- [ ] ORDER BY is applied before OFFSET/LIMIT
- [ ] Response includes correct `count` (filtered total)
- [ ] Empty state returns `{ results: [], count: 0 }`
- [ ] No N+1 queries — batch lookups with `.in_()`
- [ ] Router accepts all filter params as `Query(default=None)`
