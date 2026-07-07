"""One-off: copy a school (SCHOOL_ID) from OLD account DB to a TARGET DB,
preserving UUIDs/emails/password hashes. Backfills academic_year_id (env AY_ID)
for staff_subjects/salary_advances/route_assignments when the target requires it.
Env: SCHOOL_ID, AY_ID, TARGET_HOST, TARGET_PORT, TARGET_USER, TARGET_PASSWORD,
     TARGET_DB, DRY_RUN=1 to roll back.
"""
import os
import sys

import pymysql

SID = os.environ["SCHOOL_ID"]
AY_ID = os.environ["AY_ID"]
BACKFILL_AY = {"staff_subjects", "salary_advances", "route_assignments"}
DRY_RUN = os.environ.get("DRY_RUN") == "1"
BATCH = 500

OLD = dict(host="acela.proxy.rlwy.net", port=27874, user="root",
           password="sFDAgppEyEybUSnVOugRryYaLlhkaUxV", database="railway", charset="utf8mb4")
TGT = dict(host=os.environ["TARGET_HOST"], port=int(os.environ["TARGET_PORT"]),
           user=os.environ["TARGET_USER"], password=os.environ.get("TARGET_PASSWORD", ""),
           database=os.environ["TARGET_DB"], charset="utf8mb4", autocommit=False)


def main() -> None:
    old = pymysql.connect(**OLD)
    new = pymysql.connect(**TGT)
    try:
        with new.cursor() as c:
            c.execute("SELECT COUNT(*) FROM schools WHERE id=%s", (SID,))
            if c.fetchone()[0] > 0:
                print(f"ABORT: school {SID} already present in target.")
                sys.exit(2)

        with new.cursor() as c:
            c.execute("SELECT table_name, column_name FROM information_schema.columns "
                      "WHERE table_schema=DATABASE()")
            new_cols: dict[str, set] = {}
            for t, col in c.fetchall():
                new_cols.setdefault(t, set()).add(col)

        with old.cursor() as c:
            c.execute("SELECT table_name FROM information_schema.columns "
                      "WHERE table_schema=DATABASE() AND column_name='school_id' ORDER BY table_name")
            scoped_tables = [r[0] for r in c.fetchall()]

        def copy_table(table: str, where: str) -> int:
            ncols = new_cols.get(table)
            if not ncols:
                print(f"  SKIP {table}: not in target")
                return 0
            with old.cursor(pymysql.cursors.DictCursor) as c:
                c.execute(f"SELECT * FROM `{table}` WHERE {where}")
                rows = c.fetchall()
            if not rows:
                return 0
            src_cols = list(rows[0].keys())
            cols = [col for col in src_cols if col in ncols]
            add_ay = table in BACKFILL_AY and "academic_year_id" in ncols and "academic_year_id" not in cols
            insert_cols = cols + (["academic_year_id"] if add_ay else [])
            collist = ",".join(f"`{c}`" for c in insert_cols)
            ph = ",".join(["%s"] * len(insert_cols))
            sql = f"INSERT INTO `{table}` ({collist}) VALUES ({ph})"
            data = []
            for r in rows:
                vals = [r[col] for col in cols]
                if add_ay:
                    vals.append(AY_ID)
                data.append(vals)
            with new.cursor() as cur:
                for i in range(0, len(data), BATCH):
                    cur.executemany(sql, data[i:i + BATCH])
            return len(rows)

        with new.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=0")
            c.execute("SET UNIQUE_CHECKS=0")

        total = copy_table("schools", f"id='{SID}'")
        print(f"schools: {total}")
        for t in scoped_tables:
            n = copy_table(t, f"school_id='{SID}'")
            if n:
                total += n
        with new.cursor() as c:
            c.execute("SET FOREIGN_KEY_CHECKS=1")
            c.execute("SET UNIQUE_CHECKS=1")

        if DRY_RUN:
            new.rollback()
            print(f"[DRY_RUN] Rolled back. Would copy {total} rows for {SID}.")
        else:
            new.commit()
            print(f"✅ Committed {total} rows for {SID}.")
    except Exception as e:
        new.rollback()
        print("ROLLED BACK due to error:", repr(e))
        raise
    finally:
        old.close()
        new.close()


if __name__ == "__main__":
    main()
