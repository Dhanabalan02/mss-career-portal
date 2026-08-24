from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)


def utcnow() -> datetime:
    """Naive UTC timestamp. All datetime columns are stored in UTC so that
    values written by the app server and values written by the DB server
    agree regardless of either machine's local clock/timezone config."""
    return datetime.utcnow()


def to_ist(dt):
    """Convert a naive UTC datetime (as stored in the DB) to naive IST for
    display. Plain `date` values pass through unchanged since they carry no
    timezone-dependent instant."""
    if dt is None or not isinstance(dt, datetime):
        return dt
    return dt + IST_OFFSET


def now_ist() -> datetime:
    return utcnow() + IST_OFFSET
