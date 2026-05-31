"""
Generic schema sync: compares SQLAlchemy models with the actual DB
and adds any missing tables or columns automatically.

Run via: python -m src.scripts.sync_prod_schema
"""
import asyncio
from sqlalchemy import inspect, text, Table, MetaData, Column
from sqlalchemy.schema import CreateTable, AddConstraint
from src.core.database import engine as async_engine
from src.core.base_model import Base

# Import all models so metadata is populated
import src.models  # noqa: F401


def sync_schema(sync_conn):
    """Run inside run_sync — has access to a synchronous connection."""
    inspector = inspect(sync_conn)
    existing_tables = set(inspector.get_table_names())

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            print(f"Creating table: {table.name}")
            # Create table without FK constraints to avoid collation issues
            import re
            create_sql = str(CreateTable(table).compile(dialect=sync_conn.dialect))
            # Remove FOREIGN KEY constraint lines and any preceding comma
            create_sql = re.sub(r',?\s*\n\s*CONSTRAINT\s+\S+\s+FOREIGN KEY[^\n]*', '', create_sql)
            sync_conn.execute(text(create_sql))
        else:
            existing_cols = {c["name"]: c for c in inspector.get_columns(table.name)}
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type = col.type.compile(dialect=sync_conn.dialect)
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    default = ""
                    if col.server_default:
                        default_val = col.server_default.arg
                        if hasattr(default_val, 'text'):
                            default = f" DEFAULT {default_val.text}"
                        else:
                            default = f" DEFAULT '{default_val}'"
                    sql = f"ALTER TABLE `{table.name}` ADD COLUMN `{col.name}` {col_type} {nullable}{default}"
                    print(f"Adding column: {table.name}.{col.name}")
                    sync_conn.execute(text(sql))
                else:
                    existing_col = existing_cols[col.name]
                    expected_type = col.type.compile(dialect=sync_conn.dialect).upper()
                    actual_type = existing_col["type"].compile(dialect=sync_conn.dialect).upper()

                    def normalize(t):
                        t = t.split(" CHARACTER SET")[0].split(" COLLATE")[0].strip()
                        t = t.replace("TINYINT(1)", "BOOL").replace("NUMERIC", "DECIMAL")
                        return t

                    expected_nullable = col.nullable if col.nullable is not None else True
                    actual_nullable = existing_col.get("nullable", True)

                    if normalize(expected_type) != normalize(actual_type) or expected_nullable != actual_nullable:
                        nullable = "NULL" if expected_nullable else "NOT NULL"
                        col_type = col.type.compile(dialect=sync_conn.dialect)
                        sql = f"ALTER TABLE `{table.name}` MODIFY COLUMN `{col.name}` {col_type} {nullable}"
                        print(f"Modifying column: {table.name}.{col.name}")
                        sync_conn.execute(text(sql))

    print("Schema sync complete.")


async def run():
    async with async_engine.begin() as conn:
        await conn.run_sync(sync_schema)


if __name__ == "__main__":
    asyncio.run(run())
