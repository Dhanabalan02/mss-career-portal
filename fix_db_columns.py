"""One-time schema migration for the career portal database.

Run: python fix_db_columns.py
"""
from sqlalchemy import text
from app.core.database import engine


def col_exists(conn, table: str, col: str) -> bool:
    result = conn.execute(text(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() "
        f"AND TABLE_NAME = '{table}' AND COLUMN_NAME = '{col}'"
    ))
    return result.scalar() > 0


def drop_foreign_keys_for_column(conn, table: str, col: str) -> None:
    constraints = conn.execute(text(
        "SELECT DISTINCT CONSTRAINT_NAME "
        "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = DATABASE() "
        "AND TABLE_NAME = :table_name "
        "AND COLUMN_NAME = :column_name "
        "AND REFERENCED_TABLE_NAME IS NOT NULL"
    ), {"table_name": table, "column_name": col}).scalars().all()
    for constraint in constraints:
        conn.execute(text(
            f"ALTER TABLE {table} DROP FOREIGN KEY `{constraint}`"
        ))
        print(f"  Removed foreign key {constraint} from {table}.{col}")


JOB_APPLICANT_COLS = [
    ("masset_synced_at",   "TIMESTAMP NULL"),
    ("masset_synced_by",   "INT NULL"),
    ("masset_employee_id", "VARCHAR(100) NULL"),
]

DUPLICATE_OFFER_COLS = [
    "offered_salary",
    "joining_date",
    "probation_period",
    "offer_issued_date",
    "offer_expiry_date",
    "offer_remarks",
    "offer_template",
    "offer_letter_doc",
    "offer_letter_doc_path",
    "issued_by",
]

with engine.connect() as conn:
    for col in DUPLICATE_OFFER_COLS:
        if col_exists(conn, "job_applicants", col):
            drop_foreign_keys_for_column(conn, "job_applicants", col)
            conn.execute(text(f"ALTER TABLE job_applicants DROP COLUMN {col}"))
            print(f"  Removed duplicate job_applicants.{col}")
        else:
            print(f"  job_applicants.{col} already removed")

    for col, defn in JOB_APPLICANT_COLS:
        if not col_exists(conn, "job_applicants", col):
            conn.execute(text(f"ALTER TABLE job_applicants ADD COLUMN {col} {defn}"))
            print(f"  Added job_applicants.{col}")
        else:
            print(f"  job_applicants.{col} already exists")

    # MASSET sync remains part of the accepted-offer stage. Normalize any old
    # onboarding values before removing that value from the database enum.
    try:
        conn.execute(text(
            "UPDATE job_applicants SET applicant_stage = 'offer_accepted' "
            "WHERE applicant_stage = 'onboarding'"
        ))
        conn.execute(text(
            "ALTER TABLE job_applicants MODIFY COLUMN applicant_stage "
            "ENUM('prescreen-reject','screened','interview','offer','offer_accepted','onboarded') NULL"
        ))
        print("  Removed applicant_stage 'onboarding' value")
    except Exception as e:
        print(f"  applicant_stage enum update: {e}")

    # Add masset_synced_by FK if column just added and FK doesn't exist
    fk_check = conn.execute(text(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = DATABASE() "
        "AND TABLE_NAME = 'job_applicants' "
        "AND COLUMN_NAME = 'masset_synced_by' "
        "AND REFERENCED_TABLE_NAME = 'admins'"
    ))
    if fk_check.scalar() == 0 and col_exists(conn, "job_applicants", "masset_synced_by"):
        try:
            conn.execute(text(
                "ALTER TABLE job_applicants "
                "ADD CONSTRAINT fk_masset_synced_by "
                "FOREIGN KEY (masset_synced_by) REFERENCES admins(admin_id)"
            ))
            print("  Added FK: job_applicants.masset_synced_by -> admins.admin_id")
        except Exception as e:
            print(f"  FK masset_synced_by skipped: {e}")

    # Also update offer_acceptance_status enum to include 'rejected' if missing
    try:
        conn.execute(text(
            "ALTER TABLE job_applicants "
            "MODIFY COLUMN offer_acceptance_status "
            "ENUM('pending','accepted','expired','rejected') NULL DEFAULT 'pending'"
        ))
        print("  Updated offer_acceptance_status enum to include 'rejected'")
    except Exception as e:
        print(f"  offer_acceptance_status enum: {e}")

    conn.commit()
    print("Migration complete.")
