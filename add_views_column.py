from sqlalchemy import text
from app.core.database import SessionLocal

db = SessionLocal()
try:
    db.execute(text("ALTER TABLE job_posts ADD COLUMN views INT DEFAULT 0;"))
    db.commit()
    print("Added views column successfully!")
except Exception as e:
    print(f"Error (column might already exist): {e}")
finally:
    db.close()
