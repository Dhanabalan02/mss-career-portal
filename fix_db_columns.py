"""
One-time migration: adds new columns to admins and job_applicants tables.
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


JOB_APPLICANT_COLS = [
    ("offer_issued_date",  "DATE NULL"),
    ("offer_expiry_date",  "DATE NULL"),
    ("offer_remarks",      "TEXT NULL"),
    ("offer_template",     "VARCHAR(100) NULL"),
    ("masset_synced_at",   "TIMESTAMP NULL"),
    ("masset_synced_by",   "INT NULL"),
    ("masset_employee_id", "VARCHAR(100) NULL"),
]

with engine.connect() as conn:
    for col, defn in JOB_APPLICANT_COLS:
        if not col_exists(conn, "job_applicants", col):
            conn.execute(text(f"ALTER TABLE job_applicants ADD COLUMN {col} {defn}"))
            print(f"  Added job_applicants.{col}")
        else:
            print(f"  job_applicants.{col} already exists")

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
